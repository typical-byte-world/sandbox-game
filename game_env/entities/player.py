import pygame

from game_env.settings import (
    WIDTH,
    HEIGHT,
    PLAYER_COLOR,
    PLAYER_HEIGHT,
    PLAYER_WIDTH,
    PLAYER_ACCELERATION,
    PLAYER_MAX_SPEED,
    PLAYER_DRAG,
    PLAYER_PIXEL_SIZE,
)

from game_env.entities.bullet import Bullet
from game_env.pixel_art import draw_pixel_sprite, PLAYER_SPRITE


class Player:
    def __init__(self):
        # --------------------------------
        # Physical state
        # --------------------------------

        self.position = pygame.Vector2(
            WIDTH / 2,
            HEIGHT - 60,
        )

        self.velocity = pygame.Vector2(0, 0)
        self.acceleration = pygame.Vector2(0, 0)

        # --------------------------------
        # Collision / rendering rectangle
        # --------------------------------

        self.rect = pygame.Rect(
            0,
            0,
            PLAYER_WIDTH,
            PLAYER_HEIGHT,
        )

        self.rect.center = self.position

        # --------------------------------
        # Shooting
        # --------------------------------

        self.shoot_cooldown = 0
        self.shoot_delay = 0.2

        self.pixel_size = PLAYER_PIXEL_SIZE

    def apply_action(self, action):
        direction = pygame.Vector2(
            action.move_x,
            action.move_y,
        )

        # Prevent diagonal movement from being faster
        if direction.length_squared() > 0:
            direction = direction.normalize()

        self.acceleration = direction * PLAYER_ACCELERATION

    def update(self, dt):
        # --------------------------------
        # Velocity
        # --------------------------------

        self.velocity += self.acceleration * dt

        # Limit total velocity
        if self.velocity.length() > PLAYER_MAX_SPEED:
            self.velocity.scale_to_length(PLAYER_MAX_SPEED)

        # --------------------------------
        # Drag / friction
        # --------------------------------

        if self.acceleration.length_squared() == 0:
            self.velocity *= PLAYER_DRAG ** (dt * 60)

        # --------------------------------
        # Position
        # --------------------------------

        self.position += self.velocity * dt

        # --------------------------------
        # Keep player inside screen
        # --------------------------------

        half_width = self.rect.width / 2
        half_height = self.rect.height / 2

        if self.position.x < half_width:
            self.position.x = half_width

            if self.velocity.x < 0:
                self.velocity.x = 0

        elif self.position.x > WIDTH - half_width:
            self.position.x = WIDTH - half_width

            if self.velocity.x > 0:
                self.velocity.x = 0

        if self.position.y < half_height:
            self.position.y = half_height

            if self.velocity.y < 0:
                self.velocity.y = 0

        elif self.position.y > HEIGHT - half_height:
            self.position.y = HEIGHT - half_height

            if self.velocity.y > 0:
                self.velocity.y = 0

        # --------------------------------
        # Sync Rect with physical position
        # --------------------------------

        self.rect.center = self.position

        # --------------------------------
        # Shooting cooldown
        # --------------------------------

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
        draw_pixel_sprite(
            screen,
            PLAYER_SPRITE,
            self.position,
            self.pixel_size,
            PLAYER_COLOR,
        )