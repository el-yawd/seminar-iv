"""Carrega datasets e gera partições federadas determinísticas a partir da semente."""
from pathlib import Path

import numpy as np

DATA_DIR = Path(__file__).parent / "data"
N_CLIENTS = 100
MIN_SIZE = 5          # ao menos 1 amostra de teste local na divisão 80/20
LOCAL_TRAIN = 0.8
MAX_TRIES = 100_000

# média e desvio padrão do treino, por canal
NORM = {"fmnist": ((0.2860,), (0.3530,)),
        "cifar10": ((0.4914, 0.4822, 0.4465), (0.2470, 0.2435, 0.2616))}


def _download(name):
    import torchvision
    root = DATA_DIR / "raw"
    cls = {"fmnist": torchvision.datasets.FashionMNIST,
           "cifar10": torchvision.datasets.CIFAR10}[name]
    tr, te = cls(root, train=True, download=True), cls(root, train=False, download=True)
    def arr(ds):
        x = np.asarray(ds.data, dtype=np.uint8)
        if x.ndim == 3:
            x = x[:, None]                     # N,1,28,28
        else:
            x = x.transpose(0, 3, 1, 2)        # N,3,32,32
        return x, np.asarray(ds.targets, dtype=np.int64)
    (xtr, ytr), (xte, yte) = arr(tr), arr(te)
    np.savez_compressed(DATA_DIR / f"{name}.npz", xtr=xtr, ytr=ytr, xte=xte, yte=yte)


def load(name):
    f = DATA_DIR / f"{name}.npz"
    if not f.exists():
        DATA_DIR.mkdir(exist_ok=True)
        _download(name)
    d = np.load(f)
    return d["xtr"], d["ytr"], d["xte"], d["yte"]


def normalize(x, name):
    mean, std = (np.asarray(v, dtype=np.float32)[None, :, None, None] for v in NORM[name])
    return (x.astype(np.float32) / 255.0 - mean) / std


def dirichlet(y, alpha, rng, k=N_CLIENTS):
    """Para cada classe c, p_c ~ Dir_K(alpha). Re-sorteia até todo cliente ter >= MIN_SIZE."""
    classes = np.unique(y)
    by_class = [rng.permutation(np.flatnonzero(y == c)) for c in classes]
    for tries in range(1, MAX_TRIES + 1):
        counts = np.stack([rng.multinomial(len(ix), rng.dirichlet(alpha * np.ones(k)))
                           for ix in by_class], axis=1)          # k x C
        if counts.sum(axis=1).min() >= MIN_SIZE:
            break
    else:
        raise RuntimeError(f"alpha={alpha}: nenhuma partição válida")
    parts = [[] for _ in range(k)]
    for c, ix in enumerate(by_class):
        cuts = np.cumsum(counts[:, c])[:-1]
        for i, chunk in enumerate(np.split(ix, cuts)):
            parts[i].extend(chunk.tolist())
    return [np.asarray(p, dtype=np.int64) for p in parts], tries


def pathological(y, n_cls, rng, k=N_CLIENTS):
    """Cada cliente recebe n_cls classes; as amostras de cada classe são divididas entre seus donos."""
    C = len(np.unique(y))
    owners = [[] for _ in range(C)]
    labels = np.concatenate([rng.permutation(C) for _ in range(k * n_cls // C + 1)])[: k * n_cls]
    for i in range(k):
        for c in labels[i * n_cls:(i + 1) * n_cls]:
            owners[c].append(i)
    parts = [[] for _ in range(k)]
    for c in range(C):
        ix = rng.permutation(np.flatnonzero(y == c))
        for o, chunk in zip(owners[c], np.array_split(ix, len(owners[c]))):
            parts[o].extend(chunk.tolist())
    return [np.asarray(p, dtype=np.int64) for p in parts], 1


def quantity(y, rng, k=N_CLIENTS, scale=1.0):
    """Rótulos IID; tamanhos proporcionais a uma exponencial (mínimo MIN_SIZE)."""
    w = rng.exponential(scale, k)
    sizes = np.maximum(MIN_SIZE, np.floor(w / w.sum() * len(y))).astype(int)
    sizes[np.argmax(sizes)] -= sizes.sum() - len(y)
    ix = rng.permutation(len(y))
    return np.split(ix, np.cumsum(sizes)[:-1]), 1


def make_partitions(y, partition, alpha, seed):
    """Retorna (treino local, teste local) por cliente e o número de sorteios usados."""
    rng = np.random.default_rng([seed, 1])
    if partition == "dirichlet":
        parts, tries = dirichlet(y, alpha, rng)
    elif partition == "pathological":
        parts, tries = pathological(y, 2, rng)
    elif partition == "quantity":
        parts, tries = quantity(y, rng)
    else:
        raise ValueError(partition)
    train, test = [], []
    for p in parts:
        p = rng.permutation(p)
        n = int(round(LOCAL_TRAIN * len(p)))
        train.append(p[:n]); test.append(p[n:])
    return train, test, tries
