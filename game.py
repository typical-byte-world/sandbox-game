import pygame
import sys
from parameters import FPS, Colors, spaceship_path
from parameters import screen_height, screen_width
from spaceship import Spaceship

pygame.init()
surface = pygame.display.set_mode((screen_width, screen_height))
surf_rect = surface.get_rect()
clock = pygame.time.Clock()

space = Spaceship(220, 220, spaceship_path)


def main():
    while True:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:
            space.move_left()

        if keys[pygame.K_RIGHT]:
            space.move_right()

        if keys[pygame.K_UP]:
            space.move_up()

        if keys[pygame.K_DOWN]:
            space.move_down()

        surface.fill(Colors.YELLOW)
        surface.blit(space.image, space.rect)
        space.update()

        pygame.display.update()
        clock.tick(FPS)


if __name__ == '__main__':
    main()
