"""Imprime as linhas LaTeX das Tabelas tab:sanidade e tab:piloto a partir de results/piloto_resumo.json."""
import json
from pathlib import Path

r = json.loads((Path(__file__).parent / "results" / "piloto_resumo.json").read_text())


def br(x, d):
    return f"{x:.{d}f}".replace(".", "{,}")


nomes = ["FedAvg × FedProx $\\mu = 0$ ($\\alpha = 0{,}1$)",
         "FedAvg × FedProx $\\mu = 0$ ($\\alpha = 100$)"]
print("% tab:sanidade")
for n, s in zip(nomes, r["sanidade"]):
    d = "0" if s["max_dacc"] == 0 else f"\\num{{{s['max_dacc']:.1e}}}".replace(".", ",")
    print(f"        {n} & {'sim' if s['mesmos_clientes'] else 'não'} & {s['rodadas_identicas']}/{s['rodadas']} & {d} \\\\")

print("% tab:piloto")
prev = None
for e in sorted(r["execucoes"], key=lambda e: (e["alpha"], -1 if e["mu"] is None else e["mu"])):
    alg = "FedAvg" if e["estrategia"] == "fedavg" else f"FedProx $\\mu = {br(e['mu'], 2 if e['mu'] == 0.01 else (1 if e['mu'] == 0.1 else 0))}$"
    a = br(e["alpha"], 1) if e["alpha"] < 1 else f"{e['alpha']:g}"
    if prev is not None and prev != e["alpha"]:
        print("        \\midrule")
    prev = e["alpha"]
    print(f"        {a} & {alg} & {br(100*e['acc_final'],1)} & {br(100*e['instab'],1)} & {br(100*e['local_p10'],1)} & {br(e['t_epoca_med_s'],2)} \\\\")
