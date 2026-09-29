import pygame

from settings import (
    WIDTH,
    HEIGHT,
    PLAYER_COLOR,
    PLAYER_HEIGHT,
    PLAYER_WIDTH,
    PLAYER_ACCELERATION,
    PLAYER_MAX_SPEED,
    PLAYER_DRAG,
)
from entities.bullet import Bullet


class Player:
    def __init__(self):
        self.position = pygame.Vector2(
            WIDTH / 2,
            HEIGHT - 60,
        )

        self.velocity = pygame.Vector2(0, 0)
        self.acceleration = pygame.Vector2(0, 0)

        self.rect = pygame.Rect(
            0,
            0,
            PLAYER_WIDTH,
            PLAYER_HEIGHT,
        )

        self.rect.center = self.position

        self.shoot_cooldown = 0
        self.shoot_delay = 0.2

    def update(self, dt):
        keys = pygame.key.get_pressed()

        direction = 0

        if keys[pygame.K_LEFT]:
            direction -= 1

        if keys[pygame.K_RIGHT]:
            direction += 1

        # Acceleration
        self.acceleration.x = direction * PLAYER_ACCELERATION

        # Velocity
        self.velocity += self.acceleration * dt

        self.velocity.x = max(
            -PLAYER_MAX_SPEED,
            min(self.velocity.x, PLAYER_MAX_SPEED),
        )

        # Drag
        if direction == 0:
            self.velocity.x *= PLAYER_DRAG ** (dt * 60)

        # Position
        self.position += self.velocity * dt

        # Keep inside screen
        half_width = self.rect.width / 2

        self.position.x = max(
            half_width,
            min(self.position.x, WIDTH - half_width),
        )

        # Sync collision rectangle with physical position
        self.rect.center = self.position

        # Shooting cooldown
        self.shoot_cooldown = max(
            0,
            self.shoot_cooldown - dt,
        )

    def shoot(self):
        if self.shoot_cooldown > 0:
            return None

        self.shoot_cooldown = self.shoot_delay

        return Bullet(
            self.position.x,
            self.rect.top,
        )

    def draw(self, screen):
        pygame.draw.rect(
            screen,
            PLAYER_COLOR,
            self.rect,
        )