import pygame

from game_env.settings import (
    WIDTH,
    HEIGHT,
    BOSS_MAX_HEALTH,
    BOSS_MAX_SPEED,
    BOSS_ACCELERATION,
    BOSS_DRAG,
    BOSS_MIN_DISTANCE,
    BOSS_MAX_DISTANCE,
    BOSS_SHOOT_DELAY,
    BOSS_DASH_COOLDOWN,
    BOSS_DASH_SPEED,
    BOSS_DASH_DURATION,
)

from game_env.pixel_art import (
    BOSS_SPRITE,
    draw_pixel_sprite,
)

from game_env.entities.enemy_bullet import EnemyBullet


class Boss:
    def __init__(self, x, y):
        name = "_boss1"
        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(0, 0)
        self.acceleration = pygame.Vector2(0, 0)

        self.max_health = BOSS_MAX_HEALTH
        self.health = BOSS_MAX_HEALTH

        self.color = (255, 80, 180)
        self.pixel_size = 6

        self.rect = pygame.Rect(
            0,
            0,
            len(BOSS_SPRITE[0]) * self.pixel_size,
            len(BOSS_SPRITE) * self.pixel_size,
        )

        self.rect.center = self.position

        self.is_alive = True

        self.shoot_cooldown = 0

        self.dash_cooldown = BOSS_DASH_COOLDOWN
        self.dash_timer = 0
        self.is_dashing = False

    def update(self, dt, game):
        self.shoot_cooldown = max(
            0,
            self.shoot_cooldown - dt,
        )

        self.dash_cooldown = max(
            0,
            self.dash_cooldown - dt,
        )

        if self.is_dashing:
            self.update_dash(dt)

        else:
            self.update_movement(
                dt,
                game.player.position,
            )

            self.try_dash(
                game.player.position,
            )

        self.position += self.velocity * dt

        self.handle_screen_collision()

        self.rect.center = self.position

    def update_movement(self, dt, target_position):
        direction = target_position - self.position
        distance = direction.length()

        if distance < BOSS_MIN_DISTANCE:
            direction *= -1

        elif distance > BOSS_MAX_DISTANCE:
            pass

        else:
            direction = pygame.Vector2(0, 0)

        if direction.length_squared() > 0:
            direction = direction.normalize()

        self.acceleration = (
            direction * BOSS_ACCELERATION
        )

        self.velocity += self.acceleration * dt

        if self.velocity.length() > BOSS_MAX_SPEED:
            self.velocity.scale_to_length(
                BOSS_MAX_SPEED
            )

        self.velocity *= BOSS_DRAG ** (dt * 60)

    def try_dash(self, target_position):
        if self.dash_cooldown > 0:
            return

        direction = target_position - self.position

        if direction.length_squared() == 0:
            return

        direction = direction.normalize()

        self.velocity = (
            direction * BOSS_DASH_SPEED
        )

        self.is_dashing = True
        self.dash_timer = BOSS_DASH_DURATION
        self.dash_cooldown = BOSS_DASH_COOLDOWN

    def update_dash(self, dt):
        self.dash_timer -= dt

        if self.dash_timer <= 0:
            self.is_dashing = False

            if self.velocity.length() > BOSS_MAX_SPEED:
                self.velocity.scale_to_length(
                    BOSS_MAX_SPEED
                )

    def shoot(self):
        if self.shoot_cooldown > 0:
            return None

        self.shoot_cooldown = BOSS_SHOOT_DELAY

        return EnemyBullet(
            self.position.x,
            self.rect.bottom,
        )

    def take_damage(self, damage):
        self.health -= damage

        if self.health <= 0:
            self.health = 0
            self.is_alive = False

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
            BOSS_SPRITE,
            self.position,
            self.pixel_size,
            self.color,
        )