import pygame

from code.settings import BULLET_HEIGHT, BULLET_SPEED, BULLET_WIDTH


class Bullet:
    def __init__(self, x, y):
        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(0, -BULLET_SPEED)

        self.rect = pygame.Rect(
            0,
            0,
            BULLET_WIDTH,
            BULLET_HEIGHT,
        )

    def update(self, dt):
        self.position += self.velocity * dt

        self.rect.center = self.position

    def draw(self, screen):
        pygame.draw.rect(screen, (255, 255, 255), self.rect)