import pygame

from code.settings import (
    WIDTH,
    HEIGHT,
    SCOUT_MAX_SPEED,
    SCOUT_ACCELERATION,
    SCOUT_DRAG,
)

from code.pixel_art import (
    SCOUT_SPRITE,
    draw_pixel_sprite,
)


class Scout:
    def __init__(self, x, y, color, wave):
        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(0, 0)
        self.acceleration = pygame.Vector2(0, 0)

        self.color = color
        self.pixel_size = 3

        self.speed_multiplier = min(
            1 + (wave - 1) * 0.15,
            2.0,
        )

        sprite_width = len(SCOUT_SPRITE[0]) * self.pixel_size
        sprite_height = len(SCOUT_SPRITE) * self.pixel_size

        self.rect = pygame.Rect(
            0,
            0,
            sprite_width,
            sprite_height,
        )

        self.rect.center = self.position
        self.is_alive = True

    def update(self, dt, game):
        target_position = game.player.position

        direction = target_position - self.position

        if direction.length_squared() > 0:
            direction = direction.normalize()

        acceleration = SCOUT_ACCELERATION * self.speed_multiplier

        self.acceleration = direction * acceleration

        self.velocity += self.acceleration * dt

        max_speed = SCOUT_MAX_SPEED * self.speed_multiplier

        if self.velocity.length() > max_speed:
            self.velocity.scale_to_length(max_speed)

        self.velocity *= SCOUT_DRAG ** (dt * 60)

        self.position += self.velocity * dt

        self.handle_screen_collision()

        self.rect.center = self.position

    def handle_screen_collision(self):
        half_width = self.rect.width / 2
        half_height = self.rect.height / 2

        if self.position.x < half_width:
            self.position.x = half_width
            self.velocity.x *= -1

        if self.position.x > WIDTH - half_width:
            self.position.x = WIDTH - half_width
            self.velocity.x *= -1

        if self.position.y < half_height:
            self.position.y = half_height
            self.velocity.y *= -1

        if self.position.y > HEIGHT - half_height:
            self.position.y = HEIGHT - half_height
            self.velocity.y *= -1

    def shoot(self):
        return None

    def draw(self, screen):
        draw_pixel_sprite(
            screen,
            SCOUT_SPRITE,
            self.position,
            self.pixel_size,
            self.color,
        )