import pygame
from parameters import spaceship_move_speed, screen_width, screen_height


class Spaceship(pygame.sprite.Sprite):
    def __init__(self, x, y, filename):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.image = pygame.image.load(filename)
        self.rect = self.image.get_rect(center=(self.x, self.y))
        self.speed = spaceship_move_speed

        # self.damage = 0
        # self.bullet_speed = 0

    def update_rect(self):
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def update(self, x=None, y=None) -> None:
        pass

    def move_left(self):
        if (self.x - self.speed) > 0:
            self.x -= self.speed
        else:
            self.x = 0
        self.update_rect()

    def move_right(self):
        if (self.x + self.speed) < screen_width:
            self.x += self.speed
        else:
            self.x = screen_width
        self.update_rect()

    def move_up(self):
        if (self.y - self.speed) < screen_height:
            self.y -= self.speed
        else:
            self.y = screen_height
        self.update_rect()

    def move_down(self):
        if (self.y + self.speed) > 0:
            self.y += self.speed
        else:
            self.y = 0
        self.update_rect()

    def shoot(self):
        pass
