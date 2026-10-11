"""Q-value network used by DQN."""

from torch import nn


class QNetwork(nn.Module):
    def __init__(self, input_size, action_count):
        super().__init__()

        self.model = nn.Sequential(
            nn.Linear(input_size, 128),
            nn.ReLU(),
            nn.Linear(128, 128),
            nn.ReLU(),
            nn.Linear(128, action_count),
        )

    def forward(self, states):
        return self.model(states)
