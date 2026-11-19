"""Avalia o bloco G (gate da reformulação; ver docs/plano-reformulacao.md, seção 5).

Critério: com alpha = 0,1, a reformulação segue se, em pelo menos 2 das 3 sementes,
  Δacc(E=10) - Δacc(E=2) >= 1 p.p.   ou   ΔP10(E=10) - ΔP10(E=2) >= 3 p.p.,
onde Δ = FedProx(mu=0,1) - FedAvg na mesma semente; acc = média das rodadas 46-50.
"""
import json
from pathlib import Path

import pandas as pd

R = Path(__file__).parent / "results"
SEEDS, EPOCHS = range(3), (2, 5, 10)


def key(strat, E, seed):
    mu = "_mu0.1" if strat == "fedprox" else ""
    return f"fmnist_dirichlet_a0.1_{strat}{mu}_E{E}_s{seed}_T50"


def metrics(k):
    df = pd.read_csv(R / f"{k}.csv")
    js = json.loads((R / f"{k}.json").read_text())
    last = df[df["round"] > 45]
    return dict(acc=100 * last.acc.mean(), instab=100 * df[df["round"] > 30].acc.std(ddof=1),
                p10=100 * js["local_acc_p10"], t_round=df[df["round"] >= 2].t_round.mean(),
                wall_min=js["wall_time_s"] / 60)


rows = []
for s in SEEDS:
    for E in EPOCHS:
        try:
            a, p = metrics(key("fedavg", E, s)), metrics(key("fedprox", E, s))
        except FileNotFoundError:
            continue
        rows.append(dict(seed=s, E=E, acc_avg=a["acc"], acc_prox=p["acc"], d_acc=p["acc"] - a["acc"],
                         p10_avg=a["p10"], p10_prox=p["p10"], d_p10=p["p10"] - a["p10"],
                         instab_avg=a["instab"], instab_prox=p["instab"],
                         t_round_avg=a["t_round"], wall_min=a["wall_min"]))
df = pd.DataFrame(rows)
pd.set_option("display.width", 200)
print(df.round(2).to_string(index=False))

votes = []
for s in SEEDS:
    d = df[df.seed == s].set_index("E")
    if not {2, 10} <= set(d.index):
        continue
    acc_gain = d.d_acc[10] - d.d_acc[2]
    p10_gain = d.d_p10[10] - d.d_p10[2]
    ok = acc_gain >= 1 or p10_gain >= 3
    votes.append(ok)
    print(f"semente {s}: Δacc(E10)-Δacc(E2) = {acc_gain:+.2f} p.p.; ΔP10(E10)-ΔP10(E2) = {p10_gain:+.2f} p.p. -> {'sim' if ok else 'não'}")
print(f"\nsementes completas: {len(votes)}/3; a favor: {sum(votes)}")
if len(votes) == 3:
    print("DECISÃO:", "REFORMULAR (seguir o plano)" if sum(votes) >= 2 else "MANTER o plano original")
summary = dict(rows=rows, votes=votes, decision=None if len(votes) < 3 else bool(sum(votes) >= 2))
(R / "gate_resumo.json").write_text(json.dumps(summary, indent=2))
