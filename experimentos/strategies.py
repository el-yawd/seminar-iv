"""Estratégias do servidor com sorteio pareado de clientes e registro por rodada."""
import csv
import time

import numpy as np
from flwr.common import FitIns, ndarrays_to_parameters
from flwr.server.strategy import FedAvg, FedAvgM, FedAdam, FedProx


def paired(base):
    """Envolve uma estratégia do Flower para que, dada a semente, toda estratégia
    treine exatamente as mesmas partições em cada rodada e agregue na mesma ordem."""

    class Paired(base):
        def __init__(self, *, run_cfg, log_path, sort_results=True, **kw):
            super().__init__(**kw)
            self.run_cfg, self.log_path, self.sort_results = run_cfg, log_path, sort_results
            self.fit_log, self._t0 = {}, None

        def configure_fit(self, server_round, parameters, client_manager):
            c = self.run_cfg
            rng = np.random.default_rng([c["seed"], 2, server_round])
            pids = sorted(rng.choice(c["n_clients"], c["per_round"], replace=False).tolist())
            nodes = client_manager.sample(num_clients=len(pids), min_num_clients=len(pids))
            base_cfg = {k: c[k] for k in ("dataset", "parts", "seed", "epochs", "lr", "batch")}
            mu = float(getattr(self, "proximal_mu", 0.0))
            self._t0 = time.perf_counter()
            return [(n, FitIns(parameters, {**base_cfg, "round": server_round, "pid": p,
                                            "proximal_mu": mu}))
                    for n, p in zip(nodes, pids)]

        def configure_evaluate(self, server_round, parameters, client_manager):
            return []  # avaliação centralizada apenas

        def aggregate_fit(self, server_round, results, failures):
            if failures:
                raise RuntimeError(f"rodada {server_round}: {len(failures)} falhas")
            if self.sort_results:   # soma em ponto flutuante depende da ordem
                results = sorted(results, key=lambda r: r[1].metrics["pid"])
            m = [r[1].metrics for r in results]
            self.fit_log[server_round] = {
                "pids": " ".join(str(x["pid"]) for x in m),
                "t_epoch_mean": float(np.mean([x["t_epoch_mean"] for x in m])),
                "t_epoch_max": float(np.max([x["t_epoch_max"] for x in m])),
                "bytes_up": int(sum(sum(a.nbytes for a in _arrays(r[1].parameters))
                                    for r in results)),
                "t_round": time.perf_counter() - self._t0,
            }
            return super().aggregate_fit(server_round, results, failures)

    Paired.__name__ = f"Paired{base.__name__}"
    return Paired


def _arrays(params):
    from flwr.common import parameters_to_ndarrays
    return parameters_to_ndarrays(params)


STRATEGIES = {"fedavg": paired(FedAvg), "fedprox": paired(FedProx),
              "fedavgm": paired(FedAvgM), "fedadam": paired(FedAdam)}


def make(name, mu, init_weights, run_cfg, log_path, evaluate_fn, sort_results=True):
    kw = dict(fraction_fit=0.0, fraction_evaluate=0.0, min_fit_clients=run_cfg["per_round"],
              min_available_clients=run_cfg["n_clients"], evaluate_fn=evaluate_fn,
              initial_parameters=ndarrays_to_parameters(init_weights),
              run_cfg=run_cfg, log_path=log_path, sort_results=sort_results)
    if name == "fedprox":
        kw["proximal_mu"] = mu
    elif name == "fedavgm":
        kw.update(server_learning_rate=1.0, server_momentum=0.9)
    elif name == "fedadam":
        kw.update(eta=1e-2, beta_1=0.9, beta_2=0.99, tau=1e-3)
    return STRATEGIES[name](**kw)


class RoundWriter:
    FIELDS = ["round", "acc", "loss", "t_epoch_mean", "t_epoch_max", "t_round", "bytes_up", "pids"]

    def __init__(self, path):
        self.f = open(path, "w", newline="")
        self.w = csv.DictWriter(self.f, fieldnames=self.FIELDS)
        self.w.writeheader()

    def write(self, row):
        self.w.writerow({k: row.get(k, "") for k in self.FIELDS})
        self.f.flush()
