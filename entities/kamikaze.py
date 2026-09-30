import pygame

from settings import (
    WIDTH,
    HEIGHT,
    KAMIKAZE_MAX_SPEED,
    KAMIKAZE_ACCELERATION,
    KAMIKAZE_DRAG,
    KAMIKAZE_DETECTION_RADIUS,
    KAMIKAZE_ATTACK_DISTANCE,
)

from pixel_art import (
    KAMIKAZE_SPRITE,
    draw_pixel_sprite,
)


class Kamikaze:
    SEARCH = "search"
    CHASE = "chase"
    ATTACK = "attack"

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

        self.state = self.SEARCH

        sprite_width = len(KAMIKAZE_SPRITE[0]) * self.pixel_size
        sprite_height = len(KAMIKAZE_SPRITE) * self.pixel_size

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

        distance = self.position.distance_to(
            target_position
        )

        self.update_state(distance)

        if self.state == self.SEARCH:
            self.search(dt)

        elif self.state == self.CHASE:
            self.chase(
                dt,
                target_position,
            )

        elif self.state == self.ATTACK:
            self.attack(
                dt,
                target_position,
            )

        self.position += self.velocity * dt

        self.handle_screen_collision()

        self.rect.center = self.position

    def update_state(self, distance):
        if distance > KAMIKAZE_DETECTION_RADIUS:
            self.state = self.SEARCH

        elif distance > KAMIKAZE_ATTACK_DISTANCE:
            self.state = self.CHASE

        else:
            self.state = self.ATTACK

    def search(self, dt):
        self.acceleration = pygame.Vector2(0, 0)

        self.velocity *= KAMIKAZE_DRAG ** (dt * 60)

    def chase(self, dt, target_position):
        direction = target_position - self.position

        if direction.length_squared() > 0:
            direction = direction.normalize()

        acceleration = (
            KAMIKAZE_ACCELERATION
            * self.speed_multiplier
        )

        self.acceleration = direction * acceleration

        self.velocity += self.acceleration * dt

        max_speed = (
            KAMIKAZE_MAX_SPEED
            * self.speed_multiplier
        )

        if self.velocity.length() > max_speed:
            self.velocity.scale_to_length(max_speed)

        self.velocity *= KAMIKAZE_DRAG ** (dt * 60)

    def attack(self, dt, target_position):
        direction = target_position - self.position

        if direction.length_squared() > 0:
            direction = direction.normalize()

        acceleration = (
            KAMIKAZE_ACCELERATION
            * 1.5
            * self.speed_multiplier
        )

        self.acceleration = direction * acceleration

        self.velocity += self.acceleration * dt

        max_speed = (
            KAMIKAZE_MAX_SPEED
            * 1.5
            * self.speed_multiplier
        )

        if self.velocity.length() > max_speed:
            self.velocity.scale_to_length(max_speed)

        self.velocity *= KAMIKAZE_DRAG ** (dt * 60)

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
            KAMIKAZE_SPRITE,
            self.position,
            self.pixel_size,
            self.color,
        )