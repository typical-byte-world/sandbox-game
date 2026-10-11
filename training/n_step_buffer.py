
from collections import deque
from dataclasses import dataclass

import numpy as np


@dataclass
class NStepTransition:
    state: np.ndarray
    action: int
    reward: float
    next_state: np.ndarray
    terminated: bool
    n_steps: int


class NStepBuffer:
    def __init__(self, n_steps=5, gamma=0.99):
        if n_steps < 1:
            raise ValueError("n_steps must be >= 1")

        if not 0 <= gamma <= 1:
            raise ValueError("gamma must be between 0 and 1")

        self.n_steps = n_steps
        self.gamma = gamma
        self.pending = deque()

    def add(
        self,
        state,
        action,
        reward,
        next_state,
        terminated=False,
        truncated=False,
    ):
        if self.pending and self.pending[-1][4]:
            raise RuntimeError("Terminal transition not flushed")

        self.pending.append((
            np.asarray(state, dtype=np.float32).copy(),
            int(action),
            float(reward),
            np.asarray(next_state, dtype=np.float32).copy(),
            bool(terminated),
        ))

        completed = []

        if terminated or truncated:
            while self.pending:
                completed.append(self._build_transition())
                self.pending.popleft()

        elif len(self.pending) >= self.n_steps:
            completed.append(self._build_transition())
            self.pending.popleft()

        return completed

    def _build_transition(self):
        total_reward = 0.0
        actual_steps = 0
        final_next_state = None
        final_terminated = False

        for transition in list(self.pending)[:self.n_steps]:
            state, action, reward, next_state, terminated = transition

            total_reward += (
                self.gamma ** actual_steps
            ) * reward

            actual_steps += 1
            final_next_state = next_state
            final_terminated = terminated

            if terminated:
                break

        first_state, first_action, *_ = self.pending[0]

        return NStepTransition(
            state=first_state,
            action=first_action,
            reward=total_reward,
            next_state=final_next_state,
            terminated=final_terminated,
            n_steps=actual_steps,
        )

    def reset(self):
        self.pending.clear()

    def __len__(self):
        return len(self.pending)
