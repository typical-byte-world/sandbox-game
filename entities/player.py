import pygame

from settings import (
    HEIGHT,
    WIDTH,
    PLAYER_COLOR,
    PLAYER_HEIGHT,
    PLAYER_SPEED,
    PLAYER_WIDTH,
    PLAYER_ACCELERATION,
    PLAYER_MAX_SPEED,
    PLAYER_DRAG
)
from entities.bullet import Bullet



class Player:
    def __init__(self):
        self.rect = pygame.Rect(
            (WIDTH - PLAYER_WIDTH) // 2,
            HEIGHT - 60,
            PLAYER_WIDTH,
            PLAYER_HEIGHT,
        )

        self.velocity_x = 0.0
        self.shoot_cooldown = 0
        self.shoot_delay = 0.2


    def update(self, dt):
        keys = pygame.key.get_pressed()

        direction = 0

        if keys[pygame.K_LEFT]:
            direction -= 1

        if keys[pygame.K_RIGHT]:
            direction += 1

        # Розгін
        self.velocity_x += direction * PLAYER_ACCELERATION * dt

        # Максимальна швидкість
        self.velocity_x = max(
            -PLAYER_MAX_SPEED,
            min(self.velocity_x, PLAYER_MAX_SPEED)
        )

        # Якщо не натискаємо кнопку — гальмуємо
        if direction == 0:
            self.velocity_x *= PLAYER_DRAG ** (dt * 60)

        # Рух
        self.rect.x += self.velocity_x * dt

        # Межі екрану
        self.rect.clamp_ip(pygame.Rect(0, 0, WIDTH, HEIGHT))

        self.shoot_cooldown = max(0, self.shoot_cooldown - dt)

    def shoot(self):
        if self.shoot_cooldown > 0:
            return None

        self.shoot_cooldown = self.shoot_delay

        return Bullet(
            self.rect.centerx,
            self.rect.top,
        )


    def draw(self, screen):
        pygame.draw.rect(screen, PLAYER_COLOR, self.rect)