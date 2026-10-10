
import random

from game_env.controllers.action import Action


class RandomController:
    def __init__(self):
        self.steps = 0
        self.actions = Action.all_actions()

    def choose_action(self, state):
        self.steps += 1
        return random.choice(self.actions)
