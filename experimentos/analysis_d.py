"""Análise do bloco D (confirmatório para H1): FedProx com mu* contra FedAvg nos cinco alpha.

    python analysis_d.py                      # F-MNIST, results/
    python analysis_d.py --dataset cifar10 --resumo-a results/blocoA_cifar10_resumo.json

Sementes 5-14, partição de Dirichlet, E = 2, T = 100. Para cada alpha, com os mesmos
procedimentos do bloco C (analysis_bc.py):
  - Δ pareado (FedProx − FedAvg na mesma semente e na mesma máquina), IC 95 % e 90 % por bootstrap;
  - Wilcoxon pareado bilateral (n = 10), com correção de Holm sobre os cinco alpha;
  - TOST com delta = 1 p.p. (dois Wilcoxon unilaterais; p_TOST = o maior dos dois).
Os Δ de acurácia são arredondados a 4 casas antes dos testes, como no bloco C.

H1 (Metodologia, tab:hipoteses) é aceita se Δ > 0 for significativo (Holm) para alpha <= 0,1 e
houver equivalência (TOST) para alpha >= 1.

Cada alpha é classificado pela regra eq:mapa da Proposta: equivalente se p_TOST < 0,05; senão,
"FedProx prejudica" se Δ < 0 com p_Holm < 0,05; senão, se Δ > 0 com p_Holm < 0,05, ganho
(o custo C_tau depende do micro-experimento de H4, ainda não feito: "ganho, custo a medir");
senão, inconclusivo.

Grava results/blocoD_resumo.json.
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import wilcoxon

from analysis import r_tau
from analysis_bc import ci, load_runs, paired, tost

HERE = Path(__file__).parent


def holm(ps):
    order = sorted(range(len(ps)), key=lambda i: ps[i])
    out, running = [None] * len(ps), 0.0
    for rank, i in enumerate(order):
        running = max(running, min(1.0, (len(ps) - rank) * ps[i]))
        out[i] = running
    return out


def classify(r, level=0.05):
    if r["p_tost"] < level:
        return "equivalente"
    if r["p_holm"] < level and r["d_acc"] < 0:
        return "FedProx prejudica"
    if r["p_holm"] < level and r["d_acc"] > 0:
        return "ganho, custo a medir"
    return "inconclusivo"


def block_d(folder, dataset, mu_star, tau, delta):
    df = load_runs(folder, f"{dataset}_dirichlet_*_E2_s*_T100.json", set(range(5, 15)),
                   ("fedavg", "fedprox"))
    df = df[(df.strategy == "fedavg") | np.isclose(df.mu.fillna(-1), mu_star)]
    df["label"] = df.strategy
    df["R_tau"] = [r_tau(c, tau) for c in df.curve]
    j = paired(df, ["alpha"], "fedavg", "fedprox")
    out = []
    for alpha, g in j.groupby("alpha"):
        d = np.round(g.d_acc.to_numpy(), 4)  # ver analysis_bc.block_c
        r = dict(alpha=float(alpha), n_pairs=len(g), hosts=sorted(set(g.host_b)),
                 acc_avg=float(g.acc_b.mean()), acc_prox=float(g.acc_o.mean()),
                 acc_sd_avg=float(g.acc_b.std(ddof=1)), acc_sd_prox=float(g.acc_o.std(ddof=1)),
                 d_acc=float(d.mean()), d_acc_min=float(d.min()), d_acc_max=float(d.max()),
                 ci95=ci(d, 95), ci90=ci(d, 90),
                 p_wilcoxon=float(wilcoxon(d).pvalue), p_tost=tost(d, delta),
                 prox_wins=int((d > 0).sum()), ties=int((d == 0).sum()))
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
    for r, p in zip(out, holm([r["p_wilcoxon"] for r in out])):
        r["p_holm"] = p
        r["cell"] = classify(r)
    low = [r for r in out if r["alpha"] <= 0.1]
    high = [r for r in out if r["alpha"] >= 1]
    h1 = dict(gain_significant_alpha_le_0_1={f"{r['alpha']:g}": r["p_holm"] < 0.05 and r["d_acc"] > 0 for r in low},
              equivalent_alpha_ge_1={f"{r['alpha']:g}": r["p_tost"] < 0.05 for r in high})
    h1["accepted"] = all(h1["gain_significant_alpha_le_0_1"].values()) and all(h1["equivalent_alpha_ge_1"].values())
    return dict(dataset=dataset, mu_star=mu_star, tau=tau, delta=delta, n_runs=len(df),
                h1=h1, results=out)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--dataset", default="fmnist")
    p.add_argument("--resumo-a", default="results/blocoA_resumo.json", help="tau e mu* do bloco A")
    p.add_argument("--d", default="results", help="pasta do bloco D")
    p.add_argument("--delta", type=float, default=1.0, help="margem do TOST (p.p.)")
    p.add_argument("--name", default="blocoD")
    a = p.parse_args()
    ra = json.loads((HERE / a.resumo_a).read_text())
    res = block_d(HERE / a.d, a.dataset, ra["mu_star"], ra["tau"], a.delta)
    (HERE / "results" / f"{a.name}_resumo.json").write_text(json.dumps(res, indent=1))

    print(f"Bloco D ({res['n_runs']} execuções), mu* = {res['mu_star']}, tau = {res['tau']:.2f}, "
          f"delta = {a.delta} p.p.")
    cols = ["alpha", "n_pairs", "acc_avg", "acc_prox", "d_acc", "d_acc_min", "d_acc_max", "prox_wins",
            "ties", "p_wilcoxon", "p_holm", "p_tost", "d_p10", "d_instab", "R_tau_hit_avg",
            "R_tau_hit_prox", "R_tau_avg", "R_tau_prox", "cell"]
    t = pd.DataFrame(res["results"])
    pd.set_option("display.width", 250)
    print(t[cols].round(4).to_string(index=False))
    print("IC 95 % de Δ:", {f"{r['alpha']:g}": [round(x, 3) for x in r["ci95"]] for r in res["results"]})
    print("IC 95 % de ΔP10:", {f"{r['alpha']:g}": [round(x, 2) for x in r["ci95_p10"]] for r in res["results"]})
    print("H1:", json.dumps(res["h1"]))


if __name__ == "__main__":
    main()
