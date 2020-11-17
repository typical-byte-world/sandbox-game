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
        self.direction = 1
        self.x = float(self.rect.x)
        self.y = float(self.rect.y)

    def blitme(self):
        self.screen.blit(self.image, self.rect)

    def update(self):
        self.rect.x += self.settings.alien_speed * self.direction

    def is_alien_near_to_edge(self):
        screen_rect = self.screen.get_rect()
        if self.rect.right >= screen_rect.right or self.rect.left <= 0:
            return True
        return False

    def change_direction(self):
        self.direction = self.direction * -1
        self.rect.y += self.settings.alien_speed_y



