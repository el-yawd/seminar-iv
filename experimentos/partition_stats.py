"""Estatísticas das partições de Fashion-MNIST (semente 0): tamanhos, classes por cliente, sorteios."""
import json, sys, time
import numpy as np
import data

_, y, _, _ = data.load(sys.argv[1] if len(sys.argv) > 1 else "fmnist")
rows = []
for part, alpha in [("dirichlet", a) for a in (0.05, 0.1, 0.5, 1, 100)] + [("pathological", None), ("quantity", None)]:
    t0 = time.perf_counter()
    tr, te, tries = data.make_partitions(y, part, alpha, 0)
    dt = time.perf_counter() - t0
    full = [np.concatenate([a, b]) for a, b in zip(tr, te)]
    sizes = np.array([len(p) for p in full])
    # classes que somam >= 90% das amostras do cliente
    k90 = []
    for p in full:
        c = np.sort(np.bincount(y[p], minlength=10))[::-1]
        k90.append(int(np.searchsorted(np.cumsum(c) / c.sum(), 0.9) + 1))
    assert len(np.unique(np.concatenate(full))) == len(y) == sizes.sum()
    rows.append(dict(partition=part, alpha=alpha, tries=tries, seconds=round(dt, 2),
                     size_min=int(sizes.min()), size_med=int(np.median(sizes)), size_max=int(sizes.max()),
                     k90_med=float(np.median(k90)), k90_mean=round(float(np.mean(k90)), 2)))
    print(rows[-1], flush=True)
json.dump(rows, open("results/partition_stats.json", "w"), indent=2)
