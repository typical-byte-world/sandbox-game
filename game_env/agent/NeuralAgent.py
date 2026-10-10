
import random
from pathlib import Path

import numpy as np

from game_env.agent.network import NeuralNet
from game_env.agent.training_history import TrainingHistory
from game_env.controllers.action import Action
from game_env.settings import EPSILON, ALPHA, GAMMA


class NeuralAgent:
    def __init__(self, training=True):
        self.network = NeuralNet()

        self.training = training
        self.epsilon = EPSILON if training else 0.0
        self.alpha = ALPHA
        self.gamma = GAMMA

        self.steps = 0
        self.actions = Action.all_actions()

        self.last_current_q = 0.0
        self.last_target_q = 0.0
        self.last_td_error = 0.0
        self.last_reward = 0.0
        self.last_loss = 0.0
        self.last_action_index = 0

        self.last_q_before_update = 0.0
        self.last_q_after_update = 0.0

        self.last_observation = None
        self.last_state_q_values = None
        self.last_state_hidden = None
        self.last_exploration = False

        self.history = TrainingHistory()

    def choose_action(self, state):
        self.steps += 1

        q_values = self.network.forward(state)

        self.last_state_q_values = q_values.copy()
        self.last_state_hidden = self.network.last_a1.copy()

        if self.training and random.random() < self.epsilon:
            self.last_exploration = True
            action_index = random.randrange(len(self.actions))
        else:
            self.last_exploration = False

            max_q = np.max(q_values)
            best_indices = np.flatnonzero(q_values == max_q)
            action_index = int(random.choice(best_indices))

        self.last_action_index = action_index
        return self.actions[action_index]


    def update_q_values(
        self,
        state,
        action,
        reward,
        next_state,
        done=False,
    ):
        if not self.training:
            return None

        self.last_observation = state.copy()

        # Current Q-value
        q_values = self.network.forward(state)
        action_index = self.actions.index(action)

        current_q = float(q_values[action_index])
        self.last_q_before_update = current_q

        # TD-target
        if done:
            target = float(reward)
        else:
            next_q_values = self.network.forward(next_state)
            max_next_q = float(np.max(next_q_values))

            target = (
                float(reward)
                + self.gamma * max_next_q
            )

        # Diagnostics
        self.last_current_q = current_q
        self.last_target_q = target
        self.last_td_error = target - current_q
        self.last_reward = reward
        self.last_action_index = action_index

        weights_before = self.network.weights1.copy()
        weights2_before = self.network.weights2.copy()

        # Backpropagation
        loss = self.network.train(
            state,
            action_index,
            target,
            self.alpha,
        )

        self.last_loss = loss

        # Q-value after update
        updated_q_values = self.network.forward(state)

        delta1 = np.max(
            np.abs(self.network.weights1 - weights_before)
        )

        delta2 = np.max(
            np.abs(self.network.weights2 - weights2_before)
        )

        self.last_q_after_update = float(
            updated_q_values[action_index]
        )

        # Training history
        self.history.add(
            reward,
            loss,
            float(np.max(q_values)),
        )

        return loss

    def save(self, path: str) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        np.savez(
            path,
            weights1=self.network.weights1,
            bias1=self.network.bias1,
            weights2=self.network.weights2,
            bias2=self.network.bias2,
        )

    def load(self, path: str) -> None:
        with np.load(path, allow_pickle=False) as data:
            parameters = (
                "weights1",
                "bias1",
                "weights2",
                "bias2",
            )

            for name in parameters:
                saved = data[name]
                current = getattr(self.network, name)

                if saved.shape != current.shape:
                    raise ValueError(
                        f"{name}: expected {current.shape}, "
                        f"got {saved.shape}"
                    )

                current[...] = saved

    def get_debug_data(self):
        return {
            "observation": self.last_observation,
            "q_values": self.last_state_q_values,
            "hidden": self.last_state_hidden,

            "weights1": self.network.weights1,
            "weights2": self.network.weights2,

            "gradient_weights1": (
                self.network.last_gradient_weights1
            ),
            "gradient_weights2": (
                self.network.last_gradient_weights2
            ),

            "current_q": self.last_current_q,
            "target_q": self.last_target_q,
            "q_before_update": self.last_q_before_update,
            "q_after_update": self.last_q_after_update,

            "td_error": self.last_td_error,
            "reward": self.last_reward,
            "loss": self.last_loss,
            "action_index": self.last_action_index,

            "actions": self.actions,
            "history": self.history,
            "exploration": self.last_exploration,
            "epsilon": self.epsilon,
            "training": self.training,
        }
