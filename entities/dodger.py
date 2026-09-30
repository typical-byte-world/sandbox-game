import pygame

from settings import (
    WIDTH,
    HEIGHT,
    DODGER_MAX_SPEED,
    DODGER_ACCELERATION,
    DODGER_DRAG,
    DODGER_DANGER_DISTANCE,
    DODGER_PREDICTION_TIME,
    DODGER_ATTACK_DISTANCE,
    DODGER_SHOOT_DELAY,
)

from pixel_art import (
    DODGER_SPRITE,
    draw_pixel_sprite,
)

from entities.enemy_bullet import EnemyBullet


class Dodger:
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

        self.rect = pygame.Rect(
            0,
            0,
            len(DODGER_SPRITE[0]) * self.pixel_size,
            len(DODGER_SPRITE) * self.pixel_size,
        )

        self.rect.center = self.position

        self.is_alive = True
        self.shoot_cooldown = 0

    def update(self, dt, game):
        self.shoot_cooldown = max(
            0,
            self.shoot_cooldown - dt,
        )

        dodge_direction = self.find_dodge_direction(game)

        if dodge_direction is not None:
            self.dodge(dt, dodge_direction)
        else:
            self.attack(
                dt,
                game.player.position,
            )

        self.position += self.velocity * dt

        self.handle_screen_collision()

        self.rect.center = self.position

    def find_dodge_direction(self, game):
        for bullet in game.bullets:
            if bullet.velocity.y >= 0:
                continue

            vertical_distance = self.position.y - bullet.position.y

            if vertical_distance < 0:
                continue

            if vertical_distance > 1000:
                continue

            horizontal_distance = (
                bullet.position.x - self.position.x
            )

            if abs(horizontal_distance) > DODGER_DANGER_DISTANCE:
                continue

            if horizontal_distance < 0:
                return pygame.Vector2(1, 0)

            return pygame.Vector2(-1, 0)

        return None

    def dodge(self, dt, direction):
        acceleration = (
            DODGER_ACCELERATION
            * self.speed_multiplier
        )

        self.acceleration = direction * acceleration

        self.velocity += self.acceleration * dt

        max_speed = (
            DODGER_MAX_SPEED
            * self.speed_multiplier
        )

        if self.velocity.length() > max_speed:
            self.velocity.scale_to_length(max_speed)

        self.velocity *= DODGER_DRAG ** (dt * 60)

    def attack(self, dt, target_position):
        direction = target_position - self.position

        distance = direction.length()

        if distance > DODGER_ATTACK_DISTANCE:
            if direction.length_squared() > 0:
                direction = direction.normalize()

            acceleration = (
                DODGER_ACCELERATION
                * 0.5
                * self.speed_multiplier
            )

            self.acceleration = direction * acceleration

            self.velocity += self.acceleration * dt

        else:
            self.acceleration = pygame.Vector2(0, 0)

        max_speed = (
            DODGER_MAX_SPEED
            * self.speed_multiplier
        )

        if self.velocity.length() > max_speed:
            self.velocity.scale_to_length(max_speed)

        self.velocity *= DODGER_DRAG ** (dt * 60)

    def shoot(self):
        if self.shoot_cooldown > 0:
            return None

        self.shoot_cooldown = DODGER_SHOOT_DELAY

        return EnemyBullet(
            self.position.x,
            self.rect.bottom,
        )

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

    def draw(self, screen):
        draw_pixel_sprite(
            screen,
            DODGER_SPRITE,
            self.position,
            self.pixel_size,
            self.color,
        )