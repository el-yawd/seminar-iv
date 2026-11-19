"""CNNs dos experimentos e conversão entre state_dict e lista de ndarrays (Flower)."""
from collections import OrderedDict

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F


class CNNFMNIST(nn.Module):
    """2 conv 5x5 (32, 64) + FC 128 + FC 10: 184.586 parâmetros."""
    def __init__(self):
        super().__init__()
        self.c1, self.c2 = nn.Conv2d(1, 32, 5), nn.Conv2d(32, 64, 5)
        self.f1, self.f2 = nn.Linear(64 * 4 * 4, 128), nn.Linear(128, 10)

    def forward(self, x):
        x = F.max_pool2d(F.relu(self.c1(x)), 2)
        x = F.max_pool2d(F.relu(self.c2(x)), 2)
        return self.f2(F.relu(self.f1(x.flatten(1))))


class LeNet5(nn.Module):
    """LeNet-5 do NIID-Bench para CIFAR-10: 62.006 parâmetros."""
    def __init__(self):
        super().__init__()
        self.c1, self.c2 = nn.Conv2d(3, 6, 5), nn.Conv2d(6, 16, 5)
        self.f1, self.f2, self.f3 = nn.Linear(400, 120), nn.Linear(120, 84), nn.Linear(84, 10)

    def forward(self, x):
        x = F.max_pool2d(F.relu(self.c1(x)), 2)
        x = F.max_pool2d(F.relu(self.c2(x)), 2)
        x = F.relu(self.f1(x.flatten(1)))
        return self.f3(F.relu(self.f2(x)))


def build(dataset):
    return {"fmnist": CNNFMNIST, "cifar10": LeNet5}[dataset]()


def get_weights(net):
    return [v.detach().cpu().numpy().copy() for v in net.state_dict().values()]


def set_weights(net, weights):
    sd = OrderedDict((k, torch.from_numpy(np.asarray(w))) for k, w in zip(net.state_dict(), weights))
    net.load_state_dict(sd, strict=True)


def n_params(net):
    return sum(p.numel() for p in net.parameters())
