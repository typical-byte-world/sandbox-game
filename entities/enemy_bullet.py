import pygame

from settings import (
    ENEMY_BULLET_WIDTH,
    ENEMY_BULLET_HEIGHT,
    ENEMY_BULLET_SPEED,
)


class EnemyBullet:
    def __init__(self, x, y):
        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(0, ENEMY_BULLET_SPEED)

        self.rect = pygame.Rect(
            0,
            0,
            ENEMY_BULLET_WIDTH,
            ENEMY_BULLET_HEIGHT,
        )

        self.rect.center = self.position

    def update(self, dt):
        self.position += self.velocity * dt
        self.rect.center = self.position

    def draw(self, screen):
        pygame.draw.rect(
            screen,
            (255, 100, 100),
            self.rect,
        )