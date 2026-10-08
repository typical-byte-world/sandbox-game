import pygame
from game_env.controllers.action import Action
import random


class RandomController:
    def __init__(self):
        self.steps = 0

    def get_action(self):
        self.steps += 1
        
        keys = pygame.key.get_pressed()

        move_x, move_y, shoot = random.choice([0,1]), random.choice([0,1]), random.choice([True, False])

        return Action(move_x=move_x, move_y=move_y, shoot=shoot)