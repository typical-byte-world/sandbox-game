import pygame
from game_env.controllers.action import Action



class KeyboardController:
    def __init__(self):
        ...

    def choose_action(self, state=None):
        keys = pygame.key.get_pressed()

        move_x, move_y, shoot = 0, 0, False

        if keys[pygame.K_LEFT]:
            move_x = -1

        if keys[pygame.K_RIGHT]:
            move_x = 1

        if keys[pygame.K_UP]:
            move_y = -1

        if keys[pygame.K_DOWN]:
            move_y = 1

        if keys[pygame.K_SPACE]:
            shoot = True

        return Action(move_x=move_x, move_y=move_y, shoot=shoot)