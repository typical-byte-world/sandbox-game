import pygame
import sys
from parameters import settings as st, colors
from spaceship import Spaceship
from bullet import Bullet
from pygame.sprite import Group
from enemies.alien import Alien
import random


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

    def get_screenshot(self):
        pygame.image.save(self.screen, f'screenshots/any_name_{random.randint(0, 1000)}')

    def handle_keyboard(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.get_screenshot()
            self.ship.move_left()

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.get_screenshot()

            self.ship.move_right()

        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.get_screenshot()

            self.ship.move_up()

        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.get_screenshot()

            self.ship.move_down()

        if keys[pygame.K_SPACE]:
            self.get_screenshot()

            if len(self.bullets) > self.settings.bullets_allowed:
                return
            new_bullet = Bullet(self.screen, self.ship)
            self.bullets.add(new_bullet)

    def create_aliens_flot(self):
        alien = Alien(self.screen, self.settings )
        alien_width = alien.rect.width
        available_space = self.settings.screen_width - 100  # padding for 50 px on every side
        number_aliens_available = int(available_space / (alien_width * 2))

        for al in range(number_aliens_available):
            alien = Alien(self.screen, self.settings)
            alien.x = alien_width + 50 + 2 * alien_width * al
            alien.rect.x = alien.x
            self.aliens.add(alien)

    def check_alien_edges(self):
        for al in self.aliens.sprites():
            if al.is_alien_near_to_edge():
                self.change_aliens_direction()
                break

    def change_aliens_direction(self):
        for al in self.aliens.sprites():
            al.change_direction()

    def collisions(self, bullets, aliens):
        pygame.sprite.groupcollide(bullets, aliens, True, True)

    def keep_alians(self):
        if len(self.aliens) == 0:
            self.bullets.empty()
            self.aliens.empty()
            self.create_aliens_flot()

    def ship_collisions(self):
        if pygame.sprite.spritecollide(self.ship, self.aliens, True):
            print('you loose')

    def update_screen(self):
        self.screen.fill(colors.PURPLE)
        self.ship.blitme()
        self.bullets.update()
        self.check_alien_edges()
        self.aliens.draw(self.screen)
        self.aliens.update()
        self.keep_alians()
        self.collisions(self.bullets, self.aliens)
        self.ship_collisions()

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
