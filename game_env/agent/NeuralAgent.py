import random
import numpy as np

from game_env.agent.network import NeuralNet
from game_env.agent.training_history import TrainingHistory
from game_env.controllers.action import Action
from game_env.settings import EPSILON, ALPHA, GAMMA


class NeuralAgent:
    def __init__(self):
        self.network = NeuralNet()

        self.epsilon = EPSILON
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
        q_values = self.network.forward(state)

        self.last_state_q_values = q_values.copy()
        self.last_state_hidden = self.network.last_a1.copy()

        if random.random() < self.epsilon:
            self.last_exploration = True
            return random.choice(self.actions)

        self.last_exploration = False

        max_q = np.max(q_values)

        best_indices = np.flatnonzero(
            q_values == max_q
        )

        action_index = random.choice(best_indices)

        return self.actions[action_index]

    def update_q_values(
        self,
        state,
        action,
        reward,
        next_state,
    ):
        self.steps += 1

        self.last_observation = state.copy()

        q_values = self.network.forward(state)

        action_index = self.actions.index(action)

        current_q = q_values[action_index]

        self.last_q_before_update = current_q

        next_q_values = self.network.forward(next_state)

        max_next_q = np.max(next_q_values)

        target = reward + self.gamma * max_next_q

        self.last_current_q = current_q
        self.last_target_q = target
        self.last_td_error = target - current_q
        self.last_reward = reward
        self.last_action_index = action_index

        loss = self.network.train(
            state,
            action_index,
            target,
            self.alpha,
        )

        self.last_loss = loss

        updated_q_values = self.network.forward(state)

        self.last_q_after_update = (
            updated_q_values[action_index]
        )

        self.history.add(
            reward,
            loss,
            np.max(q_values),
        )

        return loss

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
        }