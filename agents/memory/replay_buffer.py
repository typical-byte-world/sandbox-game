import random
from collections import deque
from dataclasses import dataclass

import numpy as np
import torch


@dataclass
class Transition:
    state: np.ndarray
    action: int
    reward: float
    next_state: np.ndarray
    terminated: bool
    n_steps: int


class ReplayBuffer:
    def __init__(self, capacity=20_000, seed=None):
        if capacity <= 0:
            raise ValueError("capacity must be positive")

        self.buffer = deque(maxlen=capacity)
        self.rng = random.Random(seed)

    def __len__(self):
        return len(self.buffer)

    def add(
        self,
        state,
        action,
        reward,
        next_state,
        terminated,
        n_steps=1,
    ):
        if n_steps < 1:
            raise ValueError("n_steps must be >= 1")

        self.buffer.append(
            Transition(
                state=np.asarray(state, dtype=np.float32).copy(),
                action=int(action),
                reward=float(reward),
                next_state=np.asarray(next_state, dtype=np.float32).copy(),
                terminated=bool(terminated),
                n_steps=int(n_steps),
            )
        )

    def sample(self, batch_size, device="cpu"):
        if batch_size > len(self.buffer):
            raise ValueError("Not enough transitions")

        batch = self.rng.sample(self.buffer, batch_size)

        def tensor(values, dtype):
            return torch.as_tensor(
                values,
                dtype=dtype,
                device=device,
            )

        return {
            "states": tensor(
                np.stack([t.state for t in batch]),
                torch.float32,
            ),
            "actions": tensor(
                [t.action for t in batch],
                torch.long,
            ),
            "rewards": tensor(
                [t.reward for t in batch],
                torch.float32,
            ),
            "next_states": tensor(
                np.stack([t.next_state for t in batch]),
                torch.float32,
            ),
            "terminated": tensor(
                [t.terminated for t in batch],
                torch.bool,
            ),
            "n_steps": tensor(
                [t.n_steps for t in batch],
                torch.float32,
            ),
        }
