import pygame


class Alien(pygame.sprite.Sprite):
    def __init__(self, screen, settings):
        pygame.sprite.Sprite.__init__(self)
        self.screen = screen
        self.settings = settings
        self.image = pygame.image.load(self.settings.alien_path)
        self.image = pygame.transform.scale(self.image, self.settings.alien_size)
        self.rect = self.image.get_rect()
        self.rect.x = self.settings.alien_start_position
        self.rect.y = self.settings.alien_start_position

        self.x = float(self.rect.x)
        self.y = float(self.rect.y)

    def blitme(self):
        self.screen.blit(self.image, self.rect)

