import random

import numpy as np
import torch
from torch import nn

from agents.memory.n_step_buffer import NStepBuffer
from agents.memory.replay_buffer import ReplayBuffer
from agents.networks.dqn import QNetwork
from game_env.contracts.action import Action


class DQNAgent:
    def __init__(
        self,
        input_size,
        training=True,
        n_steps=5,
        gamma=0.99,
        learning_rate=1e-4,
        batch_size=64,
        replay_capacity=20_000,
        learning_starts=1_000,
        train_frequency=4,
        target_update_frequency=1_000,
        epsilon_start=1.0,
        epsilon_end=0.05,
        epsilon_decay_steps=50_000,
        seed=42,
        device="cpu",
    ):
        self.training = training
        self.gamma = gamma
        self.batch_size = batch_size

        self.learning_starts = learning_starts
        self.train_frequency = train_frequency
        self.target_update_frequency = target_update_frequency

        self.epsilon_start = epsilon_start
        self.epsilon_end = epsilon_end
        self.epsilon_decay_steps = epsilon_decay_steps

        self.device = torch.device(device)
        self.rng = random.Random(seed)

        self.actions = Action.all_actions()
        self.action_count = len(self.actions)

        self.policy_network = QNetwork(input_size, self.action_count).to(self.device)

        self.target_network = QNetwork(input_size, self.action_count).to(self.device)

        self.target_network.load_state_dict(self.policy_network.state_dict())
        self.target_network.eval()

        self.optimizer = torch.optim.Adam(
            self.policy_network.parameters(),
            lr=learning_rate,
        )

        self.loss_function = nn.SmoothL1Loss()

        self.replay_buffer = ReplayBuffer(
            capacity=replay_capacity,
            seed=seed,
        )

        self.n_step_buffer = NStepBuffer(
            n_steps=n_steps,
            gamma=gamma,
        )

        self.environment_steps = 0
        self.gradient_steps = 0
        self.last_loss = None

    @property
    def epsilon(self):
        if not self.training:
            return 0.0

        progress = min(
            1.0,
            self.environment_steps / max(1, self.epsilon_decay_steps),
        )

        return self.epsilon_start + progress * (self.epsilon_end - self.epsilon_start)

    def choose_action(self, state):
        if self.training and (self.rng.random() < self.epsilon):
            return self.rng.choice(self.actions)

        state_tensor = torch.as_tensor(
            np.asarray(state, dtype=np.float32),
            dtype=torch.float32,
            device=self.device,
        ).unsqueeze(0)

        with torch.no_grad():
            q_values = self.policy_network(state_tensor)

        action_index = int(q_values.argmax(dim=1).item())

        return self.actions[action_index]

    def observe(
        self,
        state,
        action,
        reward,
        next_state,
        terminated,
        truncated,
    ):
        if not self.training:
            return None

        action_index = self.actions.index(action)

        transitions = self.n_step_buffer.add(
            state=state,
            action=action_index,
            reward=reward,
            next_state=next_state,
            terminated=terminated,
            truncated=truncated,
        )

        for transition in transitions:
            self.replay_buffer.add(
                state=transition.state,
                action=transition.action,
                reward=transition.reward,
                next_state=transition.next_state,
                terminated=transition.terminated,
                n_steps=transition.n_steps,
            )

        self.environment_steps += 1

        if len(self.replay_buffer) < max(
            self.batch_size,
            self.learning_starts,
        ):
            return None

        if self.environment_steps % self.train_frequency != 0:
            return None

        return self.train_step()

    def train_step(self):
        batch = self.replay_buffer.sample(
            self.batch_size,
            device=self.device,
        )

        states = batch["states"]
        actions = batch["actions"]
        rewards = batch["rewards"]
        next_states = batch["next_states"]
        terminated = batch["terminated"]
        n_steps = batch["n_steps"]

        predicted_q = (
            self.policy_network(states).gather(1, actions.unsqueeze(1)).squeeze(1)
        )

        with torch.no_grad():
            next_q = self.target_network(next_states).max(dim=1).values

            discounts = torch.pow(
                torch.full_like(n_steps, self.gamma),
                n_steps,
            )

            targets = rewards + (discounts * next_q * (~terminated).float())

        loss = self.loss_function(
            predicted_q,
            targets,
        )

        self.optimizer.zero_grad()
        loss.backward()

        torch.nn.utils.clip_grad_norm_(
            self.policy_network.parameters(),
            max_norm=10.0,
        )

        self.optimizer.step()

        self.gradient_steps += 1
        self.last_loss = float(loss.item())

        if self.gradient_steps % self.target_update_frequency == 0:
            self.target_network.load_state_dict(self.policy_network.state_dict())

        return self.last_loss

    def reset_episode(self):
        self.n_step_buffer.reset()

    def save(self, path):
        torch.save(
            {
                "policy_network": self.policy_network.state_dict(),
                "target_network": self.target_network.state_dict(),
                "optimizer": self.optimizer.state_dict(),
                "environment_steps": self.environment_steps,
                "gradient_steps": self.gradient_steps,
            },
            path,
        )

    def load(self, path):
        checkpoint = torch.load(
            path,
            map_location=self.device,
            weights_only=True,
        )

        self.policy_network.load_state_dict(checkpoint["policy_network"])
        self.target_network.load_state_dict(checkpoint["target_network"])
        self.optimizer.load_state_dict(checkpoint["optimizer"])

        self.environment_steps = checkpoint.get("environment_steps", 0)
        self.gradient_steps = checkpoint.get("gradient_steps", 0)
