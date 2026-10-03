import pygame

from code.settings import (
    WIDTH,
    HEIGHT,
    ENEMY_HEIGHT,
    ENEMY_WIDTH,
    ENEMY_SPEED,
)


class Enemy:
    def __init__(self, x, y):
        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(ENEMY_SPEED, 0)
        self.acceleration = pygame.Vector2(0, 0)

        self.rect = pygame.Rect(
            0,
            0,
            ENEMY_WIDTH,
            ENEMY_HEIGHT,
        )

        self.rect.center = self.position
        self.is_alive = True

    def update(self, dt, game):
        self.velocity += self.acceleration * dt
        self.position += self.velocity * dt

        self.handle_screen_collision()

        self.rect.center = self.position

    def handle_screen_collision(self):
        half_width = self.rect.width / 2
        half_height = self.rect.height / 2

        if self.position.x < half_width:
            self.position.x = half_width
            self.velocity.x = 0

        if self.position.x > WIDTH - half_width:
            self.position.x = WIDTH - half_width
            self.velocity.x = 0

        if self.position.y < half_height:
            self.position.y = half_height
            self.velocity.y = 0

        if self.position.y > HEIGHT - half_height:
            self.position.y = HEIGHT - half_height
            self.velocity.y = 0

    def shoot(self):
        return None

    def draw(self, screen):
        pygame.draw.rect(
            screen,
            (200, 200, 200),
            self.rect,
        )