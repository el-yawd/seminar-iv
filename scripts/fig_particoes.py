"""Gera figs/particoes.pdf: distribuição de rótulos por cliente em partições de Dirichlet.

Reproduz o particionamento por classe usado nos experimentos (para cada classe c,
p_c ~ Dir_K(alpha)) sobre um conjunto balanceado como o CIFAR-10
(10 classes x 5000 amostras), sem precisar baixar o dataset. Sorteia de novo
enquanto algum cliente ficar com menos de MIN_SIZE amostras, sem o limite de 10
tentativas do DirichletPartitioner do Flower Datasets, que não basta para
alpha = 0.05 com 100 clientes (cerca de 1 sorteio aceito a cada 2.000).
"""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

N_CLASSES, PER_CLASS, N_CLIENTS, SHOWN, SEED = 10, 5000, 100, 20, 0
MIN_SIZE, MAX_TRIES = 5, 100_000  # 5: ao menos 1 amostra de teste local na divisão 80/20
ALPHAS = [0.05, 0.5, 100]


def dirichlet_counts(alpha, rng):
    for _ in range(MAX_TRIES):
        counts = np.zeros((N_CLIENTS, N_CLASSES), dtype=int)
        for c in range(N_CLASSES):
            p = rng.dirichlet(alpha * np.ones(N_CLIENTS))
            counts[:, c] = rng.multinomial(PER_CLASS, p)
        if counts.sum(axis=1).min() >= MIN_SIZE:
            return counts
    raise RuntimeError(f"alpha={alpha}: nenhuma partição com >= {MIN_SIZE} amostras por cliente")


rng = np.random.default_rng(SEED)
fig, axes = plt.subplots(1, len(ALPHAS), figsize=(7.0, 2.3), sharey=True)
cmap = plt.get_cmap("tab10")
for ax, alpha in zip(axes, ALPHAS):
    counts = dirichlet_counts(alpha, rng)[:SHOWN]
    frac = counts / counts.sum(axis=1, keepdims=True).clip(min=1)
    left = np.zeros(SHOWN)
    for c in range(N_CLASSES):
        ax.barh(np.arange(SHOWN), frac[:, c], left=left, color=cmap(c), height=0.85)
        left += frac[:, c]
    ax.set_title(rf"$\alpha = {alpha:g}$", fontsize=9)
    ax.set_xlim(0, 1)
    ax.set_xlabel("fração das amostras", fontsize=8)
    ax.tick_params(labelsize=7)
axes[0].set_ylabel(f"cliente (primeiros {SHOWN})", fontsize=8)
axes[0].invert_yaxis()
handles = [plt.Rectangle((0, 0), 1, 1, color=cmap(c)) for c in range(N_CLASSES)]
fig.legend(handles, [str(c) for c in range(N_CLASSES)], title="classe", fontsize=7,
           title_fontsize=7, loc="center right", frameon=False)
fig.tight_layout(rect=(0, 0, 0.92, 1))
fig.savefig("figs/particoes.pdf")
