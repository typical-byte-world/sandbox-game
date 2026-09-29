import pygame

from settings import BACKGROUND_COLOR, FPS, HEIGHT, WIDTH
from entities.player import Player
from entities.enemy import Enemy
from stats import GameStats
from hud.hud import HUD



class Game:
    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Space Invaders AI")

        self.clock = pygame.time.Clock()
        self.running = True

        self.game_over = False

        self.player = Player()

        self.bullets = []

        self.enemies = [
            Enemy(WIDTH // 4, 150),
        ]

        self.stats = GameStats()
        self.hud = HUD()


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
                if event.key == pygame.K_r and self.game_over:
                    self.restart()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bullet = self.player.shoot()

                    if bullet:
                        self.bullets.append(bullet)
                        self.stats.shots_fired += 1


    def update(self, dt):
        if self.game_over:
            return
        self.stats.survival_time += dt

        self.player.update(dt)


        for bullet in self.bullets:
            bullet.update(dt)
            

        self.bullets = [
            bullet
            for bullet in self.bullets
            if bullet.rect.bottom > 0
        ]

        for bullet in self.bullets[:]:
            for enemy in self.enemies[:]:
                if bullet.rect.colliderect(enemy.rect):
                    self.bullets.remove(bullet)
                    self.enemies.remove(enemy)

                    self.stats.kills += 1
                    self.stats.shots_hit += 1
                    self.stats.score += 100

                    break

        for enemy in self.enemies:
            enemy.update(dt)

            if enemy.rect.colliderect(self.player.rect):
                self.stats.lives -= 1
                self.enemies.remove(enemy)

                if self.stats.lives <= 0:
                    self.game_over = True

                break


    def draw(self):
        self.screen.fill(BACKGROUND_COLOR)

        self.player.draw(self.screen)

        for bullet in self.bullets:
            bullet.draw(self.screen)

        for enemy in self.enemies:
            enemy.draw(self.screen)

        if self.game_over:
            self.hud.draw_game_over(
                self.screen,
                self.stats,
            )
        else:
            self.hud.draw(
                self.screen,
                self.stats,
            )
        
        pygame.display.flip()


    def restart(self):
        self.stats.reset()

        self.player = Player()

        self.bullets.clear()

        self.enemies = [
            Enemy(WIDTH // 2, 150),
        ]

        self.game_over = False