import pygame

from settings import ENEMY_HEIGHT, ENEMY_SPEED, ENEMY_WIDTH


class Enemy:
    def __init__(self, x, y):
        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(ENEMY_SPEED//10, ENEMY_SPEED//4)

        self.rect = pygame.Rect(
            0,
            0,
            ENEMY_WIDTH,
            ENEMY_HEIGHT,
        )

        self.rect.center = self.position

    def update(self, dt):
        self.position += self.velocity * dt
        self.rect.center = self.position

    def draw(self, screen):
        pygame.draw.rect(screen, (20, 200, 236), self.rect)