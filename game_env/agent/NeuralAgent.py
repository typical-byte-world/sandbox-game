import random

import numpy as np

from game_env.agent.network import NeuralNet
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

    def choose_action(self, state):
        q_values = self.network.forward(state)

        if random.random() < self.epsilon:
            return random.choice(self.actions)

        max_q = np.max(q_values)

        best_indices = np.flatnonzero(q_values == max_q)

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

        q_values = self.network.forward(state)

        action_index = self.actions.index(action)

        # current_q = q_values[action_index]

        next_q_values = self.network.forward(next_state)

        max_next_q = np.max(next_q_values)

        target = reward + self.gamma * max_next_q

        loss = self.network.train(
            state,
            action_index,
            target,
            self.alpha,
        )

        return loss