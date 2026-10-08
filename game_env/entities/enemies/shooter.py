import pygame

from game_env.settings import (
    WIDTH,
    HEIGHT,
    SHOOTER_MAX_SPEED,
    SHOOTER_ACCELERATION,
    SHOOTER_DRAG,
    SHOOTER_MIN_DISTANCE,
    SHOOTER_MAX_DISTANCE,
    SHOOTER_SHOOT_DELAY,
)

from game_env.pixel_art import (
    SHOOTER_SPRITE,
    draw_pixel_sprite,
)

from game_env.entities.enemy_bullet import EnemyBullet


class Shooter:
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

        sprite_width = len(SHOOTER_SPRITE[0]) * self.pixel_size
        sprite_height = len(SHOOTER_SPRITE) * self.pixel_size

        self.rect = pygame.Rect(
            0,
            0,
            sprite_width,
            sprite_height,
        )

        self.rect.center = self.position
        self.is_alive = True

        self.shoot_cooldown = 0

    def update(self, dt, game):
        target_position = game.player.position

        direction = pygame.Vector2(0, 0)

        vertical_distance = target_position.y - self.position.y

        if vertical_distance < SHOOTER_MIN_DISTANCE:
            direction.y = -1

        elif vertical_distance > SHOOTER_MAX_DISTANCE:
            direction.y = 1

        horizontal_distance = target_position.x - self.position.x

        if abs(horizontal_distance) > 5:
            direction.x = 1 if horizontal_distance > 0 else -1

        if direction.length_squared() > 0:
            direction = direction.normalize()

        acceleration = SHOOTER_ACCELERATION * self.speed_multiplier

        self.acceleration = direction * acceleration

        self.velocity += self.acceleration * dt

        max_speed = SHOOTER_MAX_SPEED * self.speed_multiplier

        if self.velocity.length() > max_speed:
            self.velocity.scale_to_length(max_speed)

        self.velocity *= SHOOTER_DRAG ** (dt * 60)

        self.position += self.velocity * dt

        self.handle_screen_collision()

        self.rect.center = self.position

        self.shoot_cooldown = max(
            0,
            self.shoot_cooldown - dt,
        )

    def shoot(self, target_position):
        if self.shoot_cooldown > 0:
            return None

        self.shoot_cooldown = SHOOTER_SHOOT_DELAY

        direction = pygame.Vector2(
            target_position.x - self.position.x,
            target_position.y - self.position.y,
        )

        if direction.length_squared() == 0:
            return None

        direction = direction.normalize()

        return EnemyBullet(
            self.position.x,
            self.rect.bottom,
            direction,
        )

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

    def draw(self, screen):
        draw_pixel_sprite(
            screen,
            SHOOTER_SPRITE,
            self.position,
            self.pixel_size,
            self.color,
        )