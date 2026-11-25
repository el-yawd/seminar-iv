"""Executa uma configuração e grava results/<chave>.csv (por rodada) e <chave>.json (resumo).

Exemplo:
    python run.py --dataset fmnist --partition dirichlet --alpha 0.1 \
        --strategy fedprox --mu 0.01 --seed 0 --rounds 20
"""
import argparse
import json
import os
import platform
import sys
import time
from pathlib import Path

os.environ.setdefault("RAY_DEDUP_LOGS", "0")
HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
os.environ["PYTHONPATH"] = str(HERE) + os.pathsep + os.environ.get("PYTHONPATH", "")

import numpy as np
import torch

import data
import models
import strategies

RESULTS = HERE / "results"


def key_of(a):
    mu = f"_mu{a.mu:g}" if a.strategy == "fedprox" else ""
    alpha = f"_a{a.alpha:g}" if a.partition == "dirichlet" else ""
    tag = "_unsorted" if a.unsorted else ""
    return f"{a.dataset}_{a.partition}{alpha}_{a.strategy}{mu}_E{a.epochs}_s{a.seed}_T{a.rounds}{tag}"


def cpu_model():
    """Modelo da CPU (identifica a máquina que gerou o resultado; platform.processor() é vazio no Linux)."""
    try:
        for line in Path("/proc/cpuinfo").read_text().splitlines():
            if line.startswith("model name"):
                return line.split(":", 1)[1].strip()
    except OSError:
        pass
    return platform.processor() or platform.machine()


def evaluate(net, x, y, batch=1000):
    net.eval()
    correct, loss = 0, 0.0
    ce = torch.nn.CrossEntropyLoss(reduction="sum")
    with torch.no_grad():
        for i in range(0, len(y), batch):
            out = net(x[i:i + batch])
            loss += ce(out, y[i:i + batch]).item()
            correct += (out.argmax(1) == y[i:i + batch]).sum().item()
    return correct / len(y), loss / len(y)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--dataset", default="fmnist", choices=["fmnist", "cifar10"])
    p.add_argument("--partition", default="dirichlet", choices=["dirichlet", "pathological", "quantity"])
    p.add_argument("--alpha", type=float, default=0.1)
    p.add_argument("--strategy", default="fedavg", choices=list(strategies.STRATEGIES))
    p.add_argument("--mu", type=float, default=0.0)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--rounds", type=int, default=100)
    p.add_argument("--epochs", type=int, default=2)
    p.add_argument("--lr", type=float, default=0.01)
    p.add_argument("--batch", type=int, default=32)
    p.add_argument("--clients", type=int, default=data.N_CLIENTS)
    p.add_argument("--per-round", type=int, default=10)
    p.add_argument("--unsorted", action="store_true", help="não ordena os resultados antes de agregar (diagnóstico)")
    p.add_argument("--force", action="store_true")
    p.add_argument("--out", default="results",
                   help="pasta dos resultados, relativa a experimentos/ (outra máquina refazendo um FedAvg já existente)")
    a = p.parse_args()

    global RESULTS
    RESULTS = HERE / a.out
    RESULTS.mkdir(parents=True, exist_ok=True)
    key = key_of(a)
    if (RESULTS / f"{key}.json").exists() and not a.force:
        print(f"[skip] {key}")
        return
    t_start = time.perf_counter()

    # partição determinística, salva para os clientes
    xtr, ytr, xte, yte = data.load(a.dataset)
    data.normalized_train(a.dataset); data.train_labels(a.dataset)  # cria o cache antes dos atores
    tr, te, tries = data.make_partitions(ytr, a.partition, a.alpha, a.seed)
    parts_dir = data.DATA_DIR / "parts"; parts_dir.mkdir(exist_ok=True)
    part_key = f"{a.dataset}_{a.partition}" + (f"_a{a.alpha:g}" if a.partition == "dirichlet" else "") + f"_s{a.seed}"
    parts_path = parts_dir / f"{part_key}.npz"
    if not parts_path.exists():
        np.savez(parts_path, train=np.array(tr, dtype=object), test=np.array(te, dtype=object))

    # avaliação centralizada no servidor
    torch.set_num_threads(4)
    torch.manual_seed(a.seed)
    net = models.build(a.dataset)
    init = models.get_weights(net)
    x_te = torch.from_numpy(data.normalize(xte, a.dataset)); y_te = torch.from_numpy(yte)
    x_tr = torch.from_numpy(data.normalize(xtr, a.dataset)); y_tr = torch.from_numpy(ytr)
    writer = strategies.RoundWriter(RESULTS / f"{key}.csv")
    state = {"strategy": None, "final": None}

    def evaluate_fn(rnd, weights, cfg):
        models.set_weights(net, weights)
        acc, loss = evaluate(net, x_te, y_te)
        row = {"round": rnd, "acc": acc, "loss": loss, **state["strategy"].fit_log.get(rnd, {})}
        writer.write(row)
        if rnd == a.rounds:  # dispersão: modelo final nos testes locais
            local = [evaluate(net, x_tr[torch.from_numpy(ix)], y_tr[torch.from_numpy(ix)])[0]
                     for ix in te if len(ix)]
            state["final"] = local
        print(f"[{key}] rodada {rnd:3d}  acc={acc:.4f}  loss={loss:.4f}", flush=True)
        return loss, {"acc": acc}

    run_cfg = dict(dataset=a.dataset, parts=str(parts_path), seed=a.seed, epochs=a.epochs,
                   lr=a.lr, batch=a.batch, n_clients=a.clients, per_round=a.per_round)
    strat = strategies.make(a.strategy, a.mu, init, run_cfg, None, evaluate_fn,
                            sort_results=not a.unsorted)
    state["strategy"] = strat

    from flwr.server import ServerApp, ServerAppComponents, ServerConfig
    from flwr.simulation import run_simulation
    from client import app as client_app

    server_app = ServerApp(server_fn=lambda ctx: ServerAppComponents(
        strategy=strat, config=ServerConfig(num_rounds=a.rounds)))
    run_simulation(server_app=server_app, client_app=client_app, num_supernodes=a.clients,
                   backend_config={"client_resources": {"num_cpus": 1,
                                                       "num_gpus": 0.1 if torch.cuda.is_available() else 0.0}})

    local = np.array(state["final"] or [np.nan])
    sizes = np.array([len(t) + len(s) for t, s in zip(tr, te)])
    summary = dict(key=key, args=vars(a), n_params=models.n_params(net), partition_tries=tries,
                   client_size_min=int(sizes.min()), client_size_max=int(sizes.max()),
                   local_acc_std=float(np.nanstd(local)), local_acc_p10=float(np.nanpercentile(local, 10)),
                   wall_time_s=time.perf_counter() - t_start,
                   env=dict(python=platform.python_version(), torch=torch.__version__,
                            cpu=platform.processor() or platform.machine(), cuda=torch.cuda.is_available(),
                            cpu_model=cpu_model(), n_cpus=os.cpu_count(), host=platform.node(),
                            gpu=torch.cuda.get_device_name(0) if torch.cuda.is_available() else None))
    (RESULTS / f"{key}.json").write_text(json.dumps(summary, indent=2))
    print(f"[done] {key} em {summary['wall_time_s']:.0f} s")


if __name__ == "__main__":
    main()
