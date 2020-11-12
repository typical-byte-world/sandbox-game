import pygame
import sys
from parameters import settings as st, colors
from spaceship import Spaceship
from bullet import Bullet
from pygame.sprite import Group
from enemies.alien import Alien


class Game:
    def __init__(self):
        pygame.init()
        self.settings = st
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((self.settings.screen_width, self.settings.screen_height))
        self.surf_rect = self.screen.get_rect()
        self.ship = Spaceship(self.screen, self.settings)
        self.bullets = Group()
        self.aliens = Group()
        self.create_aliens_flot()

    def handle_keyboard(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.ship.move_left()

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.ship.move_right()

        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.ship.move_up()

        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.ship.move_down()

        if keys[pygame.K_SPACE]:
            if len(self.bullets) > self.settings.bullets_allowed:
                return
            new_bullet = Bullet(self.screen, self.ship)
            self.bullets.add(new_bullet)

    def create_aliens_flot(self):
        alien = Alien(self.screen, self.settings)
        alien_width = alien.rect.width
        available_space = self.settings.screen_width - 100  # padding for 50 px on every side
        number_aliens_available = int(available_space / (alien_width * 2))

        for al in range(number_aliens_available):
            alien = Alien(self.screen, self.settings)
            alien.x = alien_width + 50 + 2 * alien_width * al
            alien.rect.x = alien.x
            self.aliens.add(alien)

    def update_screen(self):
        self.screen.fill(colors.PURPLE)
        self.ship.blitme()
        self.bullets.update()
        self.aliens.draw(self.screen)

        for bull in self.bullets.sprites():
            if bull.is_deletable():
                self.bullets.remove(bull)
            bull.draw_bullet()

        pygame.display.flip()

    def run_loop(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            self.handle_keyboard()
            self.update_screen()
            self.clock.tick(self.settings.FPS)


if __name__ == '__main__':
    game = Game()
    game.run_loop()
