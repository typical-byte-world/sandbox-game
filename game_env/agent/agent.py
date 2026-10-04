import random
from game_env.controllers.action import Action
from game_env.settings import EPSILON, ALPHA, GAMMA

class Agent:
    def __init__(self):
        self.q_table = {}
        self.epsilon = EPSILON
        self.alpha = ALPHA
        self.gamma = GAMMA

        self.steps = 0

    def choose_action(self, state):
        actions = self.get_q_values(state)

        if random.random() < self.epsilon:
            return random.choice(list(actions.keys()))

        max_q = max(actions.values())

        best_actions = [
            action
            for action, q in actions.items()
            if q == max_q
        ]

        return random.choice(best_actions)
        # return max(actions, key=actions.get)

    
    def get_q_values(self, state):
        if state in self.q_table:
            return self.q_table[state]

        self.q_table[state] = {action: 0 for action in Action.all_actions()}

        return self.q_table[state]



    def update_q_values(self, state, action, reward, next_state):
        self.steps += 1
        q_values = self.get_q_values(state)
        current_q = q_values[action]


        next_q_values = self.get_q_values(next_state)
        max_next_q = max(next_q_values.values())

        new_q = current_q + self.alpha * (reward + self.gamma * max_next_q - current_q)

        q_values[action] = new_q

    def get_max_q(self):
        if not self.q_table:
            return 0

        return max(
            max(actions.values())
            for actions in self.q_table.values()
        )

    def get_min_q(self):
        if not self.q_table:
            return 0

        return min(
            min(actions.values())
            for actions in self.q_table.values()
        )