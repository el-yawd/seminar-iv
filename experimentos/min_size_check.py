"""Fração de sorteios de Dirichlet (100 clientes) que atendem a um tamanho mínimo por cliente (F-MNIST, semente 0)."""
import json
import numpy as np
import data

_, y, _, _ = data.load("fmnist")
N, out = 10_000, {}
for alpha in (0.05, 0.1):
    rng = np.random.default_rng(0)
    per_class = [int((y == c).sum()) for c in range(10)]
    mins = np.empty(N, dtype=int)
    for i in range(N):
        counts = np.stack([rng.multinomial(n, rng.dirichlet(alpha * np.ones(100))) for n in per_class], axis=1)
        mins[i] = counts.sum(axis=1).min()
    out[str(alpha)] = {f"min>={m}": int((mins >= m).sum()) for m in (5, 10)}
    print(alpha, out[str(alpha)], flush=True)
json.dump({"sorteios": N, **out}, open("results/min_size_check.json", "w"), indent=2)
