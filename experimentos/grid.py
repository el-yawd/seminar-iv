"""Gera as configurações de um bloco e executa as que ainda não têm resultado (retomável).

    python grid.py --block piloto
"""
import argparse
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
ALPHAS = [0.05, 0.1, 0.5, 1, 100]
MUS = [0.01, 0.1, 1]


def block(name, dataset):
    base = dict(dataset=dataset, partition="dirichlet")
    if name == "piloto":
        # piloto (F-MNIST, semente 0, T = 20): sanidade mu = 0 e primeira passada de mu
        cfgs = []
        for alpha in (0.1, 100):
            cfgs += [dict(base, alpha=alpha, strategy="fedavg"),
                     dict(base, alpha=alpha, strategy="fedprox", mu=0.0)]
            cfgs += [dict(base, alpha=alpha, strategy="fedprox", mu=m) for m in MUS]
        return [dict(c, seed=0, rounds=20) for c in cfgs]
    if name == "A":
        return [dict(base, alpha=a, strategy=s, mu=m, seed=sd, rounds=100)
                for sd in range(5) for a in ALPHAS
                for s, m in [("fedavg", 0.0)] + [("fedprox", m) for m in MUS]]
    if name == "B":
        return [dict(base, alpha=a, strategy=s, seed=sd, rounds=100)
                for sd in range(3) for a in ALPHAS for s in ("fedavgm", "fedadam")]
    raise ValueError(name)


def to_args(c):
    out = []
    for k, v in c.items():
        if k == "unsorted":
            out += ["--unsorted"] if v else []
        else:
            out += [f"--{k}", str(v)]
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--block", required=True)
    p.add_argument("--dataset", default="fmnist")
    a = p.parse_args()
    cfgs = block(a.block, a.dataset)
    for i, c in enumerate(cfgs, 1):
        print(f"=== {i}/{len(cfgs)} {c}", flush=True)
        r = subprocess.run([sys.executable, str(HERE / "run.py"), *to_args(c)])
        if r.returncode:
            print(f"!!! falhou (código {r.returncode}); seguindo", flush=True)


if __name__ == "__main__":
    main()
