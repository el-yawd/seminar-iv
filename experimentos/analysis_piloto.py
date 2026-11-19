"""Analisa o piloto: teste de sanidade (mu = 0 vs FedAvg), curvas e tempos.

Gera figs/piloto_curvas.pdf e results/piloto_resumo.json.
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).parent
R = HERE / "results"
FIGS = HERE.parent / "figs"


def load(key):
    df = pd.read_csv(R / f"{key}.csv")
    js = json.loads((R / f"{key}.json").read_text())
    return df, js


def k(alpha, strat, mu=None, unsorted=False):
    m = f"_mu{mu:g}" if strat == "fedprox" else ""
    return f"fmnist_dirichlet_a{alpha:g}_{strat}{m}_s0_T20" + ("_unsorted" if unsorted else "")


out = {"sanidade": [], "execucoes": []}

# --- teste de sanidade ---------------------------------------------------
pairs = [("FedAvg × FedProx μ=0 (α=0,1)", k(0.1, "fedavg"), k(0.1, "fedprox", 0)),
         ("FedAvg × FedProx μ=0 (α=100)", k(100, "fedavg"), k(100, "fedprox", 0))]
for name, a, b in pairs:
    da, _ = load(a); db, _ = load(b)
    out["sanidade"].append(dict(
        par=name,
        mesmos_clientes=bool((da.pids.fillna("") == db.pids.fillna("")).all()),
        max_dacc=float((da.acc - db.acc).abs().max()),
        max_dloss=float((da.loss - db.loss).abs().max()),
        rodadas_identicas=int(((da.acc == db.acc) & (da.loss == db.loss)).sum()),
        rodadas=len(da)))

# --- execuções do piloto ---------------------------------------------------
cfgs = [(a, "fedavg", None) for a in (0.1, 100)] + \
       [(a, "fedprox", m) for a in (0.1, 100) for m in (0, 0.01, 0.1, 1)]
curves = {}
for alpha, s, mu in cfgs:
    df, js = load(k(alpha, s, mu))
    curves[(alpha, s, mu)] = df
    last = df[df["round"] > 15]
    tr = df[df["round"] >= 2]  # rodada 1 inclui o carregamento dos dados nos atores
    out["execucoes"].append(dict(
        alpha=alpha, estrategia=s, mu=mu,
        acc_final=float(last.acc.mean()), acc_max=float(df.acc.max()),
        instab=float(last.acc.std(ddof=1)), loss_final=float(df.loss.iloc[-1]),
        t_epoca_med_s=float(tr.t_epoch_mean.mean()), t_rodada_med_s=float(tr.t_round.mean()),
        t_parede_s=js["wall_time_s"], local_std=js["local_acc_std"], local_p10=js["local_acc_p10"],
        tries=js["partition_tries"], cli_min=js["client_size_min"], cli_max=js["client_size_max"]))

(R / "piloto_resumo.json").write_text(json.dumps(out, indent=2, ensure_ascii=False))
pd.set_option("display.width", 200)
print(pd.DataFrame(out["sanidade"]).to_string())
print(pd.DataFrame(out["execucoes"]).round(4).to_string())

# --- figura ----------------------------------------------------------------
plt.rcParams.update({"font.size": 8})
fig, axes = plt.subplots(1, 2, figsize=(7.0, 2.5), sharey=True)
styles = {("fedavg", None): dict(color="black", lw=1.6, label="FedAvg"),
          ("fedprox", 0): dict(color="#c26a12", lw=0, marker="o", ms=2.6, label=r"FedProx $\mu=0$"),
          ("fedprox", 0.01): dict(color="#2a78c2", lw=1.0, label=r"FedProx $\mu=0{,}01$"),
          ("fedprox", 0.1): dict(color="#2e7d4f", lw=1.0, label=r"FedProx $\mu=0{,}1$"),
          ("fedprox", 1): dict(color="#9b3fb5", lw=1.0, ls="--", label=r"FedProx $\mu=1$")}
for ax, alpha in zip(axes, (0.1, 100)):
    for (s, mu), st in styles.items():
        df = curves[(alpha, s, mu)]
        ax.plot(df["round"], 100 * df.acc, **st)
    ax.set_title(rf"$\alpha = {alpha:g}$".replace(".", "{,}"))
    ax.set_xlabel("rodada")
    ax.set_xticks(range(0, 21, 5))
    ax.grid(alpha=0.25)
axes[0].set_ylabel("acurácia global (%)")
axes[1].legend(loc="lower right", fontsize=7, frameon=False)
fig.tight_layout()
fig.savefig(FIGS / "piloto_curvas.pdf")
print("figura:", FIGS / "piloto_curvas.pdf")
