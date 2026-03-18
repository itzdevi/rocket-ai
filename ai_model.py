import torch
from torch import nn
from constants import *
from torch.distributions import *
import state

class PPOModel(nn.Module):
    def __init__(self):
        super().__init__()

        self.backbone = nn.Sequential(
            nn.Linear(INPUT_SIZE, HIDDEN_SIZE),
            nn.ReLU(),
            nn.Linear(HIDDEN_SIZE, HIDDEN_SIZE),
            nn.ReLU()
        )

        self.mu_head = nn.Linear(HIDDEN_SIZE, 2)
        self.log_sigma = nn.Parameter(torch.zeros(2))

        self.value_head = nn.Linear(HIDDEN_SIZE, 1)

    def forward(self, state: state.State):
        x = self.backbone(state)

        mu = self.mu_head(x)

        log_sigma = torch.clamp(self.log_sigma, -5, 2)
        log_sigma = log_sigma.expand_as(mu)
        sigma = torch.exp(log_sigma)

        dist_cont = Normal(mu, sigma)

        value = self.value_head(x).squeeze(-1)

        return dist_cont, value
    