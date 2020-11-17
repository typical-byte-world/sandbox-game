import pygame
from bullet import Bullet
import time


class Spaceship(pygame.sprite.Sprite):
    def __init__(self, screen, settings):
        pygame.sprite.Sprite.__init__(self)
        self.file = settings.spaceship_path
        self.settings = settings
        self.image = pygame.image.load(self.file)
        self.rect = self.image.get_rect()
        self.speed = settings.spaceship_move_speed
        self.screen = screen
        self.screen_rect = self.screen.get_rect()
        self.rect.centerx = self.screen_rect.centerx
        self.rect.bottom = self.screen_rect.bottom
        self.bullets = []

        self.last_bullet_shoot = time.time()

    def blitme(self):
        self.screen.blit(self.image, self.rect)

    def move_left(self):
        if (self.rect.left - self.speed) > -self.settings.SPRITE_PADDING:
            self.rect.left -= self.speed
        else:
            self.rect.left = 0

    def move_right(self):
        if (self.rect.right + self.speed) < self.settings.screen_width + self.settings.SPRITE_PADDING:
            self.rect.right += self.speed
        else:
            self.rect.right = self.settings.screen_width

    def move_up(self):
        if (self.rect.top - self.speed) > -self.settings.SPRITE_PADDING:
            self.rect.top -= self.speed
        else:
            self.rect.top = 0

    def move_down(self):
        if (self.rect.bottom + self.speed) < self.settings.screen_height + self.settings.SPRITE_PADDING:
            self.rect.bottom += self.speed
        else:
            self.rect.bottom = self.settings.screen_height

    def shoot(self):
        bullet = Bullet(self.rect.centerx, self.rect.centery)
        self.bullets.append(bullet)

    def update_bullets(self):
        for bull in self.bullets:
            bullet_outside_the_screen = bull.rect.bottom < -100
            if bullet_outside_the_screen:
                self.bullets.remove(bull)
                continue
            bull.move()
