
import random

import numpy as np
import torch
from torch import nn

from game_env.agent.network import NeuralNet
from game_env.controllers.action import Action
from game_env.settings import EPSILON, GAMMA


class NeuralAgent:
    def __init__(
        self,
        input_size=11,
        hidden_size=16,
        training=True,
        learning_rate=0.001,
    ):
        self.training = training
        self.epsilon = EPSILON if training else 0.0
        self.gamma = GAMMA

        self.device = torch.device("cpu")

        self.actions = Action.all_actions()

        self.network = NeuralNet(
            input_size=input_size,
            hidden_size=hidden_size,
            output_size=len(self.actions),
        ).to(self.device)

        self.optimizer = torch.optim.Adam(
            self.network.parameters(),
            lr=learning_rate,
        )

        self.loss_fn = nn.MSELoss()

        self.steps = 0

        self.last_reward = 0.0
        self.last_loss = 0.0
        self.last_td_error = 0.0
        self.last_current_q = 0.0
        self.last_target_q = 0.0

    def _to_tensor(self, state):
        return torch.as_tensor(
            np.asarray(state, dtype=np.float32),
            dtype=torch.float32,
            device=self.device,
        )

    def choose_action(self, state):
        self.steps += 1

        if (
            self.training
            and random.random() < self.epsilon
        ):
            return random.choice(self.actions)

        with torch.no_grad():
            q_values = self.network(
                self._to_tensor(state)
            )

            best_q = q_values.max()

            best_indices = torch.where(
                torch.isclose(q_values, best_q)
            )[0].tolist()

        return self.actions[
            random.choice(best_indices)
        ]

    def update_q_values(
        self,
        state,
        action,
        reward,
        next_state,
        done=False,
    ):
        if not self.training:
            return

        action_index = self.actions.index(action)

        state_tensor = self._to_tensor(state)
        next_state_tensor = self._to_tensor(next_state)

        # 1. Поточне Q(s, a)
        current_q = self.network(
            state_tensor
        )[action_index]

        # 2. TD-target
        with torch.no_grad():
            if done:
                target_q = torch.tensor(
                    float(reward),
                    dtype=torch.float32,
                    device=self.device,
                )
            else:
                next_q_values = self.network(
                    next_state_tensor
                )

                target_q = (
                    float(reward)
                    + self.gamma * next_q_values.max()
                )

        # 3. Функція втрат
        loss = self.loss_fn(
            current_q,
            target_q,
        )

        # 4. Зберігаємо діагностику ДО оновлення ваг
        self.last_reward = float(reward)
        self.last_loss = loss.item()
        self.last_current_q = current_q.item()
        self.last_target_q = target_q.item()
        self.last_td_error = (
            self.last_target_q - self.last_current_q
        )

        # 5. Backpropagation
        self.optimizer.zero_grad()
        loss.backward()

        # 6. Gradient clipping
        torch.nn.utils.clip_grad_norm_(
            self.network.parameters(),
            max_norm=10.0,
        )

        # 7. Оновлення параметрів
        self.optimizer.step()


    def save(self, path):
        torch.save(
            {
                "model_state_dict":
                    self.network.state_dict(),
                "optimizer_state_dict":
                    self.optimizer.state_dict(),
                "epsilon": self.epsilon,
                "steps": self.steps,
            },
            path,
        )

    def load(self, path):
        checkpoint = torch.load(
            path,
            map_location=self.device,
            weights_only=True,
        )

        self.network.load_state_dict(
            checkpoint["model_state_dict"]
        )

        if self.training:
            self.optimizer.load_state_dict(
                checkpoint["optimizer_state_dict"]
            )

            self.epsilon = checkpoint["epsilon"]
            self.steps = checkpoint["steps"]
