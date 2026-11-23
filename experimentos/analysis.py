"""Consolida os resultados de um bloco em métricas por execução e diferenças pareadas.

    python analysis.py                # bloco A (F-MNIST, Dirichlet, E = 2, T = 100)
    python analysis.py --dataset cifar10

Métricas por execução (Tabela tab:metricas da Metodologia):
  acc     média da acurácia global nas últimas 5 rodadas (%)
  instab  desvio padrão da acurácia global nas últimas 20 rodadas (p.p.)
  p10/sd  percentil 10 e desvio padrão da acurácia local nos 100 clientes (%)
  R_tau   primeira rodada com acurácia >= tau; None se não atingir (censurada)
tau = 90 % da acurácia final média do FedAvg com alpha = 100 no mesmo dataset
(média das sementes disponíveis).

Diferenças pareadas: Δ = FedProx(mu) − FedAvg na mesma semente. Só entram pares em
que as duas execuções existem e foram feitas na mesma máquina (o resultado não é
bit a bit igual entre máquinas; ver docs/registro-vostro.md).

Grava results/<bloco>_resumo.json. Testes de hipótese (Wilcoxon, Holm, TOST) ficam
para os blocos confirmatórios (C e D).
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

R = Path(__file__).parent / "results"


def run_metrics(csv, js):
    df = pd.read_csv(csv)
    meta = json.loads(js.read_text())
    a = meta["args"]
    acc = 100 * df.acc.to_numpy()
    return dict(
        alpha=a["alpha"], strategy=a["strategy"], mu=a["mu"] if a["strategy"] == "fedprox" else None,
        seed=a["seed"], rounds=a["rounds"],
        acc=acc[-5:].mean(), instab=np.std(acc[-20:], ddof=1),
        p10=100 * meta["local_acc_p10"], sd_local=100 * meta["local_acc_std"],
        wall_min=meta["wall_time_s"] / 60, host=meta.get("env", {}).get("host"),
        curve=acc,
    )


def load(dataset, epochs, rounds):
    rows = []
    for js in sorted(R.glob(f"{dataset}_dirichlet_*_E{epochs}_s*_T{rounds}.json")):
        csv = js.with_suffix(".csv")
        if csv.exists():
            rows.append(run_metrics(csv, js))
    return pd.DataFrame(rows)


def r_tau(curve, tau):
    hit = np.flatnonzero(curve >= tau)
    return int(hit[0]) if hit.size else None  # índice = rodada (a linha 0 é a rodada 0)


def bootstrap_ci(x, n=10000, seed=0):
    if len(x) < 3:
        return None, None
    rng = np.random.default_rng(seed)
    means = rng.choice(x, size=(n, len(x)), replace=True).mean(axis=1)
    return float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--dataset", default="fmnist")
    p.add_argument("--epochs", type=int, default=2)
    p.add_argument("--rounds", type=int, default=100)
    p.add_argument("--name", default="blocoA")
    a = p.parse_args()

    df = load(a.dataset, a.epochs, a.rounds)
    if df.empty:
        raise SystemExit("nenhum resultado encontrado")
    ref = df[(df.strategy == "fedavg") & (df.alpha == 100)]
    tau = 0.9 * ref.acc.mean() if len(ref) else None
    df["R_tau"] = [r_tau(c, tau) if tau else None for c in df.curve]

    avg = df[df.strategy == "fedavg"].set_index(["alpha", "seed"])
    pairs = []
    for _, r in df[df.strategy == "fedprox"].iterrows():
        k = (r.alpha, r.seed)
        if k not in avg.index or avg.loc[k].host != r.host:
            continue
        b = avg.loc[k]
        pairs.append(dict(alpha=r.alpha, mu=r.mu, seed=r.seed,
                          d_acc=r.acc - b.acc, d_p10=r.p10 - b.p10, d_instab=r.instab - b.instab,
                          R_tau_avg=b.R_tau, R_tau_prox=r.R_tau))
    pr = pd.DataFrame(pairs)

    # resumo por (alpha, algoritmo): médias sobre as sementes com par completo
    summary = []
    for alpha in sorted(df.alpha.unique()):
        seeds_ok = sorted(set(pr[pr.alpha == alpha].seed)) if len(pr) else []
        base = df[(df.alpha == alpha) & (df.strategy == "fedavg") & df.seed.isin(seeds_ok)]
        summary.append(dict(alpha=alpha, alg="FedAvg", n=len(base), acc=base.acc.mean(),
                            p10=base.p10.mean(), instab=base.instab.mean(),
                            R_tau_hit=f"{base.R_tau.notna().sum()}/{len(base)}"))
        for mu in sorted(pr[pr.alpha == alpha].mu.unique()):
            q = pr[(pr.alpha == alpha) & (pr.mu == mu)]
            runs = df[(df.alpha == alpha) & (df.mu == mu) & df.seed.isin(q.seed)]
            lo, hi = bootstrap_ci(q.d_acc.to_numpy())
            summary.append(dict(alpha=alpha, alg=f"mu={mu:g}", n=len(q), acc=runs.acc.mean(),
                                p10=runs.p10.mean(), instab=runs.instab.mean(),
                                d_acc=q.d_acc.mean(), d_acc_min=q.d_acc.min(), d_acc_max=q.d_acc.max(),
                                d_acc_ci95=[lo, hi], d_p10=q.d_p10.mean(), d_instab=q.d_instab.mean(),
                                R_tau_hit=f"{runs.R_tau.notna().sum()}/{len(runs)}"))
    sm = pd.DataFrame(summary)

    pd.set_option("display.width", 200)
    print(f"{a.name}: {len(df)} execuções; sementes {sorted(int(s) for s in df.seed.unique())}; máquinas {sorted(df.host.dropna().unique())}")
    print(f"tau = {tau:.2f} %  (90 % do FedAvg com alpha = 100)" if tau else "tau indefinido (sem FedAvg alpha = 100)")
    cols = ["alpha", "alg", "n", "acc", "d_acc", "d_acc_min", "d_acc_max", "p10", "d_p10", "instab", "d_instab", "R_tau_hit"]
    print(sm[[c for c in cols if c in sm]].round(2).to_string(index=False))

    out = dict(dataset=a.dataset, epochs=a.epochs, rounds=a.rounds, tau=tau,
               runs=df.drop(columns="curve").to_dict("records"),
               pairs=pr.to_dict("records"), summary=sm.to_dict("records"))
    (R / f"{a.name}_resumo.json").write_text(json.dumps(out, indent=2, default=lambda o: None if pd.isna(o) else o))


if __name__ == "__main__":
    main()
