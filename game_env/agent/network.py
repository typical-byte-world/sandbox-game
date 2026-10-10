
import torch
from torch import nn


class NeuralNet(nn.Module):
    def __init__(
        self,
        input_size=11,
        hidden_size=16,
        output_size=4,
    ):
        super().__init__()

        self.layers = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.LeakyReLU(negative_slope=0.01),
            nn.Linear(hidden_size, output_size),
        )

    def forward(self, x):
        return self.layers(x)
