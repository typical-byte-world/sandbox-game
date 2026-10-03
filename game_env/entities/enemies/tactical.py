import pygame

from game_env.settings import (
    WIDTH,
    HEIGHT,
    TACTICAL_MAX_SPEED,
    TACTICAL_ACCELERATION,
    TACTICAL_DRAG,
    TACTICAL_MIN_DISTANCE,
    TACTICAL_MAX_DISTANCE,
    TACTICAL_SEPARATION_DISTANCE,
    TACTICAL_SEPARATION_FORCE,
    TACTICAL_SHOOT_DELAY,
)

from game_env.pixel_art import (
    TACTICAL_SPRITE,
    draw_pixel_sprite,
)

from game_env.entities.enemy_bullet import EnemyBullet


class Tactical:
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
            len(TACTICAL_SPRITE[0]) * self.pixel_size,
            len(TACTICAL_SPRITE) * self.pixel_size,
        )

        self.rect.center = self.position

        self.is_alive = True
        self.shoot_cooldown = 0

    def update(self, dt, game):
        self.shoot_cooldown = max(
            0,
            self.shoot_cooldown - dt,
        )

        target_position = game.player.position

        target_direction = self.get_target_direction(
            target_position
        )

        separation_direction = self.get_separation_direction(
            game
        )

        direction = (
            target_direction
            + separation_direction * TACTICAL_SEPARATION_FORCE
        )

        if direction.length_squared() > 0:
            direction = direction.normalize()

        acceleration = (
            TACTICAL_ACCELERATION
            * self.speed_multiplier
        )

        self.acceleration = direction * acceleration

        self.velocity += self.acceleration * dt

        max_speed = (
            TACTICAL_MAX_SPEED
            * self.speed_multiplier
        )

        if self.velocity.length() > max_speed:
            self.velocity.scale_to_length(max_speed)

        self.velocity *= TACTICAL_DRAG ** (dt * 60)

        self.position += self.velocity * dt

        self.handle_screen_collision()

        self.rect.center = self.position

    def get_target_direction(self, target_position):
        direction = target_position - self.position
        distance = direction.length()

        if distance < TACTICAL_MIN_DISTANCE:
            return -direction

        if distance > TACTICAL_MAX_DISTANCE:
            return direction

        return pygame.Vector2(0, 0)

    def get_separation_direction(self, game):
        separation = pygame.Vector2(0, 0)

        for enemy in game.enemies:
            if enemy is self:
                continue

            offset = self.position - enemy.position
            distance = offset.length()

            if distance == 0:
                continue

            if distance < TACTICAL_SEPARATION_DISTANCE:
                strength = (
                    TACTICAL_SEPARATION_DISTANCE
                    - distance
                ) / TACTICAL_SEPARATION_DISTANCE

                separation += (
                    offset.normalize()
                    * strength
                )

        return separation

    def shoot(self):
        if self.shoot_cooldown > 0:
            return None

        self.shoot_cooldown = TACTICAL_SHOOT_DELAY

        return EnemyBullet(
            self.position.x,
            self.rect.bottom,
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
            TACTICAL_SPRITE,
            self.position,
            self.pixel_size,
            self.color,
        )