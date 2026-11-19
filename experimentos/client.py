"""Cliente Flower: treino local com termo proximal opcional e medição do tempo por época.

A partição a treinar vem na configuração da rodada (chave "pid"), e não do nó: o
Flower sorteia nós por ID aleatório, o que quebraria o pareamento entre algoritmos.
"""
import os
import time
from functools import lru_cache

os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")  # exigido por algoritmos determinísticos em CUDA

import numpy as np
import torch
from flwr.client import ClientApp, NumPyClient

import data
import models

torch.use_deterministic_algorithms(True)
torch.backends.cudnn.benchmark = False


def sync(device):
    if device.type == "cuda":
        torch.cuda.synchronize()


def train(net, loader, epochs, lr, mu, device):
    # cópia congelada do modelo global w^t
    w_glob = [p.detach().clone() for p in net.parameters()]
    opt = torch.optim.SGD(net.parameters(), lr=lr)
    ce = torch.nn.CrossEntropyLoss()
    times = []
    net.train()
    for _ in range(epochs):
        sync(device)
        t0 = time.perf_counter()
        for x, y in loader:
            x, y = x.to(device), y.to(device)
            opt.zero_grad()
            loss = ce(net(x), y)
            if mu > 0:  # termo proximal (FedProx)
                prox = sum((p - g).pow(2).sum() for p, g in zip(net.parameters(), w_glob))
                loss = loss + (mu / 2) * prox
            loss.backward()
            opt.step()
        sync(device)
        times.append(time.perf_counter() - t0)
    return times


@lru_cache(maxsize=2)
def _dataset(name):
    return data.normalized_train(name), data.train_labels(name)


@lru_cache(maxsize=2)
def _partitions(path):
    return np.load(path, allow_pickle=True)["train"]


class FLClient(NumPyClient):
    def fit(self, parameters, config):
        torch.set_num_threads(1)
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        name, pid = config["dataset"], int(config["pid"])
        x, y = _dataset(name)
        idx = _partitions(config["parts"])[pid]
        ds = torch.utils.data.TensorDataset(torch.from_numpy(np.ascontiguousarray(x[idx])),
                                            torch.from_numpy(y[idx]))
        g = torch.Generator().manual_seed(int(config["seed"]) * 1_000_003
                                          + int(config["round"]) * 1_009 + pid)
        loader = torch.utils.data.DataLoader(ds, batch_size=int(config["batch"]),
                                             shuffle=True, generator=g)
        net = models.build(name).to(device)
        models.set_weights(net, parameters)
        times = train(net, loader, int(config["epochs"]), float(config["lr"]),
                      float(config.get("proximal_mu", 0.0)), device)
        return models.get_weights(net), len(ds), {
            "pid": pid, "t_epoch_mean": float(np.mean(times)), "t_epoch_max": float(np.max(times))}


app = ClientApp(client_fn=lambda context: FLClient().to_client())
