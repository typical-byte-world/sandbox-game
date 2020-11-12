import pygame
from parameters import settings, colors
# to do: equal time between bullets


class Bullet(pygame.sprite.Sprite):
    def __init__(self, screen, ship):
        pygame.sprite.Sprite.__init__(self)
        self.screen = screen
        self.rect = pygame.Rect(0, 0, settings.bullet_width, settings.bullet_height)
        self.rect.centerx = ship.rect.centerx
        self.rect.top = ship.rect.top
        self.y = float(self.rect.y)
        self.color = colors.BLUE
        self.speed_factor = settings.bullet_speed

    def update(self):
        self.y -= self.speed_factor
        self.rect.y = self.y

    def draw_bullet(self):
        pygame.draw.rect(self.screen, self.color, self.rect)

    def is_deletable(self):
        if self.rect.bottom < 0:
            return True
        return False
