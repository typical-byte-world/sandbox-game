import pygame

from game_env.config.display import (
    HEIGHT,
    WIDTH,
)
from game_env.config.physics import (
    BOSS_ACCELERATION,
    BOSS_DASH_COOLDOWN,
    BOSS_DASH_DURATION,
    BOSS_DASH_SPEED,
    BOSS_DRAG,
    BOSS_HP_BAR_HEIGHT,
    BOSS_HP_BAR_WIDTH,
    BOSS_MAX_DISTANCE,
    BOSS_MAX_HEALTH,
    BOSS_MAX_SPEED,
    BOSS_MIN_DISTANCE,
    BOSS_SHOOT_DELAY,
)
from game_env.entities.enemy_bullet import EnemyBullet
from game_env.entities.motion import constrain_to_screen
from game_env.rendering.sprites import (
    BOSS_SPRITE,
    draw_pixel_sprite,
)


class Boss:
    def __init__(self, x, y):
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

        self.acceleration = direction * BOSS_ACCELERATION

        self.velocity += self.acceleration * dt

        if self.velocity.length() > BOSS_MAX_SPEED:
            self.velocity.scale_to_length(BOSS_MAX_SPEED)

        self.velocity *= BOSS_DRAG ** (dt * 60)

    def try_dash(self, target_position):
        if self.dash_cooldown > 0:
            return

        direction = target_position - self.position

        if direction.length_squared() == 0:
            return

        direction = direction.normalize()

        self.velocity = direction * BOSS_DASH_SPEED

        self.is_dashing = True
        self.dash_timer = BOSS_DASH_DURATION
        self.dash_cooldown = BOSS_DASH_COOLDOWN

    def update_dash(self, dt):
        self.dash_timer -= dt

        if self.dash_timer <= 0:
            self.is_dashing = False

            if self.velocity.length() > BOSS_MAX_SPEED:
                self.velocity.scale_to_length(BOSS_MAX_SPEED)

    def shoot(self, game):
        if self.shoot_cooldown > 0:
            return None

        direction = game.player.position - self.position

        if direction.length_squared() == 0:
            return None

        direction = direction.normalize()

        self.shoot_cooldown = BOSS_SHOOT_DELAY

        return EnemyBullet(
            self.position.x,
            self.rect.bottom,
            direction,
        )

    def take_damage(self, damage):
        self.health -= damage

        if self.health <= 0:
            self.health = 0
            self.is_alive = False

    def handle_screen_collision(self):
        constrain_to_screen(
            self.position,
            self.velocity,
            self.rect,
            WIDTH,
            HEIGHT,
            bounce=True,
        )

    def draw(self, screen):
        draw_pixel_sprite(
            screen,
            BOSS_SPRITE,
            self.position,
            self.pixel_size,
            self.color,
        )

        # hp bar
        x_bar_pos = self.position.x - (BOSS_HP_BAR_WIDTH // 2)
        y_bar_pos = self.rect.top - BOSS_HP_BAR_HEIGHT - 10
        adjusted_width = int(BOSS_HP_BAR_WIDTH * (self.health / self.max_health))

        # фон
        pygame.draw.rect(
            screen,
            (50, 50, 50),
            (x_bar_pos, y_bar_pos, BOSS_HP_BAR_WIDTH, BOSS_HP_BAR_HEIGHT),
        )
        # hp
        pygame.draw.rect(
            screen,
            (100, 100, 100),
            (x_bar_pos, y_bar_pos, adjusted_width, BOSS_HP_BAR_HEIGHT),
        )

        # рамка
        pygame.draw.rect(
            screen,
            (90, 250, 50),
            (x_bar_pos, y_bar_pos, BOSS_HP_BAR_WIDTH, BOSS_HP_BAR_HEIGHT),
            3,
        )
