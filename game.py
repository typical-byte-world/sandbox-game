import pygame

from settings import BACKGROUND_COLOR, FPS, HEIGHT, WIDTH
from entities.player import Player


class Game:
    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Space Invaders AI")

        self.clock = pygame.time.Clock()
        self.running = True

        self.player = Player()

        self.bullets = []

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000

            self.handle_events()
            self.update(dt)
            self.draw()

        pygame.quit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bullet = self.player.shoot()

                    if bullet:
                        self.bullets.append(bullet)


    def update(self, dt):
        self.player.update(dt)


        for bullet in self.bullets:
            bullet.update(dt)

        self.bullets = [
            bullet
            for bullet in self.bullets
            if bullet.rect.bottom > 0
        ]


    def draw(self):
        self.screen.fill(BACKGROUND_COLOR)

        self.player.draw(self.screen)

        for bullet in self.bullets:
            bullet.draw(self.screen)

        pygame.display.flip()