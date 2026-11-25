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
ALPHAS2 = [0.1, 1, 100]
EPOCHS = [2, 5, 10]


def rounds_for(E):
    return 100 if E <= 2 else 50


def block(name, dataset, mu_star=0.1):
    base = dict(dataset=dataset, partition="dirichlet")
    if name == "piloto":
        # piloto (F-MNIST, semente 0, T = 20): sanidade mu = 0 e primeira passada de mu
        cfgs = []
        for alpha in (0.1, 100):
            cfgs += [dict(base, alpha=alpha, strategy="fedavg"),
                     dict(base, alpha=alpha, strategy="fedprox", mu=0.0)]
            cfgs += [dict(base, alpha=alpha, strategy="fedprox", mu=m) for m in MUS]
        return [dict(c, seed=0, rounds=20) for c in cfgs]
    # --- reformulação: heterogeneidade x trabalho local (docs/plano-reformulacao.md) ---
    if name == "G":  # gate: FedAvg x FedProx mu=0,1 em alpha=0,1, E em {2,5,10}, sementes 0-2, T=50
        return [dict(base, alpha=0.1, strategy=s, mu=m, epochs=E, seed=sd, rounds=50)
                for sd in range(3) for E in EPOCHS for s, m in (("fedavg", 0.0), ("fedprox", 0.1))]
    if name == "A2":  # exploratório: (FedAvg + 3 mu) x 3 alpha x 3 E x sementes 0-2
        return [dict(base, alpha=a, strategy=s, mu=m, epochs=E, seed=sd, rounds=rounds_for(E))
                for sd in range(3) for a in ALPHAS2 for E in EPOCHS
                for s, m in [("fedavg", 0.0)] + [("fedprox", m) for m in MUS]]
    if name in ("D2", "cifar"):  # confirmatório: FedAvg x FedProx mu*, sementes 5-14
        alphas = (0.1, 100) if name == "D2" else (0.1,)
        return [dict(base, alpha=a, strategy=s, mu=m, epochs=E, seed=sd, rounds=rounds_for(E))
                for sd in range(5, 15) for a in alphas for E in (2, 10)
                for s, m in (("fedavg", 0.0), ("fedprox", mu_star))]
    if name == "A":
        return [dict(base, alpha=a, strategy=s, mu=m, seed=sd, rounds=100)
                for sd in range(5) for a in ALPHAS
                for s, m in [("fedavg", 0.0)] + [("fedprox", m) for m in MUS]]
    # --- plano original, confirmatório (Metodologia, tab:blocos): FedAvg x FedProx mu*, sementes 5-14 ---
    if name == "C":  # tipo de heterogeneidade: patológica (k = 2) e quantidade (rótulos IID)
        return [dict(dataset=dataset, partition=part, strategy=s, mu=m, seed=sd, rounds=100)
                for sd in range(5, 15) for part in ("pathological", "quantity")
                for s, m in (("fedavg", 0.0), ("fedprox", mu_star))]
    if name == "D":  # nível de heterogeneidade: 5 alpha
        return [dict(base, alpha=a, strategy=s, mu=m, seed=sd, rounds=100)
                for sd in range(5, 15) for a in ALPHAS
                for s, m in (("fedavg", 0.0), ("fedprox", mu_star))]
    if name == "B":  # referências; o FedAvg (do bloco A) só roda se faltar na pasta de saída (outra máquina)
        return [dict(base, alpha=a, strategy=s, seed=sd, rounds=100)
                for sd in range(3) for a in ALPHAS for s in ("fedavg", "fedavgm", "fedadam")]
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
    p.add_argument("--mu-star", type=float, default=0.1, help="mu* para os blocos C, D, D2 e cifar")
    p.add_argument("--shard", default="0/1",
                   help="i/n: executa só a i-ésima de n fatias de sementes (dividir entre máquinas). "
                        "A divisão é por semente, para que FedAvg e FedProx da mesma semente rodem na mesma máquina.")
    p.add_argument("--out", default="results",
                   help="pasta dos resultados (relativa a experimentos/). Ex.: bloco B em outra máquina, que "
                        "precisa refazer o FedAvg das sementes 0-2 sem sobrescrever o do bloco A")
    a = p.parse_args()
    if a.block == "cifar":
        a.dataset = "cifar10"
    cfgs = block(a.block, a.dataset, a.mu_star)
    i, n = map(int, a.shard.split("/"))
    seeds = sorted({c["seed"] for c in cfgs})[i::n]
    cfgs = [c for c in cfgs if c["seed"] in seeds]
    print(f"shard {i}/{n}: sementes {seeds}, {len(cfgs)} configurações", flush=True)
    for i, c in enumerate(cfgs, 1):
        print(f"=== {i}/{len(cfgs)} {c}", flush=True)
        r = subprocess.run([sys.executable, str(HERE / "run.py"), *to_args(c), "--out", a.out])
        if r.returncode:
            print(f"!!! falhou (código {r.returncode}); seguindo", flush=True)


if __name__ == "__main__":
    main()
