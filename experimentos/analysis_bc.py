"""Análise dos blocos B (referências) e C (tipo de heterogeneidade).

    python analysis_bc.py                      # F-MNIST: B em results/blocoB, C em results/
    python analysis_bc.py --dataset cifar10

Bloco B (descritivo, sementes 0-2): FedAvgM e FedAdam contra o FedAvg da MESMA máquina
(results/blocoB; ver --b-host-missing). Δ = estratégia − FedAvg na mesma semente; com 3 pares, reporta média,
mínimo e máximo, sem teste de hipótese (Metodologia: o B só situa a magnitude dos efeitos).

Bloco C (confirmatório para H3, sementes 5-14): FedProx com mu* contra FedAvg nas partições
patológica (k = 2) e de quantidade. Para cada partição:
  - Δ pareado, IC 95 % e IC 90 % por bootstrap;
  - Wilcoxon pareado bilateral (n = 10; com empates, o scipy usa a aproximação normal),
    com correção de Holm sobre as duas partições;
  - TOST com delta = 1 p.p.: dois Wilcoxon unilaterais, H0 Δ <= −delta e H0 Δ >= +delta;
    p_TOST = maior dos dois. Equivalência se p_TOST < 0,05.
As métricas por execução são as de analysis.py (acc = média das 5 últimas rodadas etc.).
R_tau usa o tau do bloco A do mesmo dataset (results/<nome A>_resumo.json).

Grava results/blocoB_resumo.json e results/blocoC_resumo.json.
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import wilcoxon

from analysis import bootstrap_ci, r_tau, run_metrics

HERE = Path(__file__).parent
METRICS = ("acc", "instab", "p10", "sd_local")


def load_runs(folder, pattern, seeds, strategies):
    rows = []
    for js in sorted(folder.glob(pattern)):
        csv = js.with_suffix(".csv")
        if not csv.exists():
            continue
        m = run_metrics(csv, js)
        meta = json.loads(js.read_text())["args"]
        m["partition"] = meta["partition"]
        if m["seed"] in seeds and m["strategy"] in strategies:
            rows.append(m)
    return pd.DataFrame(rows)


def paired(df, keys, base, other):
    """Pares (other − base) na mesma semente e na mesma máquina."""
    b = df[df.label == base].set_index(keys + ["seed"])
    o = df[df.label == other].set_index(keys + ["seed"])
    j = b.join(o, how="inner", suffixes=("_b", "_o"))
    j = j[j.host_b == j.host_o]
    for m in METRICS + ("R_tau",):
        j[f"d_{m}"] = j[f"{m}_o"] - j[f"{m}_b"]
    return j.reset_index()


def ci(x, level):
    x = np.asarray(x, dtype=float)
    rng = np.random.default_rng(0)
    means = rng.choice(x, size=(10000, len(x)), replace=True).mean(axis=1)
    lo = (100 - level) / 2
    return float(np.percentile(means, lo)), float(np.percentile(means, 100 - lo))


def tost(d, delta):
    p_low = wilcoxon(d + delta, alternative="greater").pvalue   # H0: Δ <= −delta
    p_high = wilcoxon(d - delta, alternative="less").pvalue     # H0: Δ >= +delta
    return float(max(p_low, p_high))


def block_b(folder, dataset, tau, host_missing):
    df = load_runs(folder, f"{dataset}_dirichlet_*_E2_s*_T100.json", {0, 1, 2},
                   ("fedavg", "fedavgm", "fedadam"))
    if host_missing:
        df["host"] = df.host.fillna(host_missing)
    df["label"] = df.strategy
    df["R_tau"] = [r_tau(c, tau) for c in df.curve]
    hosts = sorted(df.host.dropna().unique())
    summary, deltas = [], []
    for (alpha, s), g in df.groupby(["alpha", "strategy"]):
        summary.append(dict(alpha=alpha, strategy=s, n=len(g),
                            **{m: float(g[m].mean()) for m in METRICS},
                            R_tau_mean=float(g.R_tau.dropna().mean()) if g.R_tau.notna().any() else None,
                            R_tau_hit=f"{g.R_tau.notna().sum()}/{len(g)}"))
    for s in ("fedavgm", "fedadam"):
        j = paired(df, ["alpha"], "fedavg", s)
        for alpha, g in j.groupby("alpha"):
            deltas.append(dict(alpha=alpha, strategy=s, n_pairs=len(g),
                               **{f"d_{m}": float(g[f"d_{m}"].mean()) for m in METRICS},
                               d_acc_min=float(g.d_acc.min()), d_acc_max=float(g.d_acc.max())))
    return dict(dataset=dataset, folder=str(folder.relative_to(HERE)), hosts=hosts, tau=tau,
                n_runs=len(df), summary=summary, deltas=deltas)


def block_c(folder, dataset, mu_star, tau, delta):
    rows = []
    for part in ("pathological", "quantity"):
        d = load_runs(folder, f"{dataset}_{part}_*_E2_s*_T100.json", set(range(5, 15)),
                      ("fedavg", "fedprox"))
        rows.append(d)
    df = pd.concat(rows, ignore_index=True)
    df = df[(df.strategy == "fedavg") | np.isclose(df.mu.fillna(-1), mu_star)]
    df["label"] = df.strategy
    df["R_tau"] = [r_tau(c, tau) for c in df.curve]
    out = []
    j = paired(df, ["partition"], "fedavg", "fedprox")
    for part, g in j.groupby("partition"):
        # a acurácia de uma rodada é um múltiplo de 1/10000 (acertos no teste), e a média de 5 rodadas,
        # de 0,002 p.p.; arredondar remove o ruído de ponto flutuante, que desfaria os empates
        # verdadeiros entre |Δ| e levaria o scipy ao Wilcoxon exato sem empates
        d = np.round(g.d_acc.to_numpy(), 4)
        r = dict(partition=part, n_pairs=len(g), hosts=sorted(set(g.host_b)),
                 acc_avg=float(g.acc_b.mean()), acc_prox=float(g.acc_o.mean()),
                 acc_sd_avg=float(g.acc_b.std(ddof=1)), acc_sd_prox=float(g.acc_o.std(ddof=1)),
                 d_acc=float(d.mean()), d_acc_min=float(d.min()), d_acc_max=float(d.max()),
                 ci95=ci(d, 95), ci90=ci(d, 90),
                 p_wilcoxon=float(wilcoxon(d).pvalue), p_tost=tost(d, delta),
                 prox_wins=int((d > 0).sum()))
        for m in ("instab", "p10", "sd_local"):
            r[f"{m}_avg"] = float(g[f"{m}_b"].mean())
            r[f"d_{m}"] = float(g[f"d_{m}"].mean())
            r[f"ci95_{m}"] = ci(g[f"d_{m}"], 95)
        r["R_tau_hit_avg"] = f"{g.R_tau_b.notna().sum()}/{len(g)}"
        r["R_tau_hit_prox"] = f"{g.R_tau_o.notna().sum()}/{len(g)}"
        both = g.dropna(subset=["R_tau_b", "R_tau_o"])
        r["R_tau_avg"] = float(both.R_tau_b.mean()) if len(both) else None
        r["R_tau_prox"] = float(both.R_tau_o.mean()) if len(both) else None
        r["n_uncensored_pairs"] = len(both)
        r["wall_min"] = float(pd.concat([g.wall_min_b, g.wall_min_o]).mean())
        out.append(r)
    # Holm sobre a família do bloco C (as duas partições)
    order = sorted(range(len(out)), key=lambda i: out[i]["p_wilcoxon"])
    running = 0.0
    for rank, i in enumerate(order):
        running = max(running, min(1.0, (len(out) - rank) * out[i]["p_wilcoxon"]))
        out[i]["p_holm"] = running
    return dict(dataset=dataset, mu_star=mu_star, tau=tau, delta=delta, n_runs=len(df), results=out)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--dataset", default="fmnist")
    p.add_argument("--resumo-a", default="results/blocoA_resumo.json", help="tau e mu* do bloco A")
    p.add_argument("--b", default="results/blocoB", help="pasta do bloco B (FedAvg da mesma máquina)")
    p.add_argument("--c", default="results", help="pasta do bloco C")
    p.add_argument("--b-host-missing", default="melchior",
                   help="máquina atribuída às execuções do B sem env.host (gravadas antes desse campo). "
                        "As 30 de FedAvgM/FedAdam do F-MNIST rodaram no i5 (melchior): results/blocoB/B.log, "
                        "e uma delas, refeita com o código atual, reproduziu a antiga bit a bit. '' desliga.")
    p.add_argument("--delta", type=float, default=1.0, help="margem do TOST (p.p.)")
    a = p.parse_args()
    ra = json.loads((HERE / a.resumo_a).read_text())
    tau, mu_star = ra["tau"], ra["mu_star"]

    b = block_b(HERE / a.b, a.dataset, tau, a.b_host_missing)
    (HERE / "results" / "blocoB_resumo.json").write_text(json.dumps(b, indent=1))
    print(f"Bloco B ({b['n_runs']} execuções, máquinas {b['hosts']}), tau = {tau:.2f}")
    print(pd.DataFrame(b["summary"]).round(2).to_string(index=False))
    print(pd.DataFrame(b["deltas"]).round(2).to_string(index=False))

    c = block_c(HERE / a.c, a.dataset, mu_star, tau, a.delta)
    (HERE / "results" / "blocoC_resumo.json").write_text(json.dumps(c, indent=1))
    print(f"\nBloco C ({c['n_runs']} execuções), mu* = {mu_star}, delta = {a.delta} p.p.")
    for r in c["results"]:
        print(json.dumps(r, indent=1))


if __name__ == "__main__":
    main()
