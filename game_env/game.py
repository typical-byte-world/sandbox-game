import pygame

from game_env.settings import BACKGROUND_COLOR, FPS, HEIGHT, WIDTH
from game_env.entities.player import Player
from game_env.entities.enemy import Enemy
from game_env.stats import GameStats
from game_env.hud.hud import HUD
from game_env.entities.enemies.scout import Scout
from game_env.wave_manager import WaveManager
import random
from game_env.entities.enemies.shooter import Shooter
from game_env.entities.enemies.kamikaze import Kamikaze
from game_env.entities.enemies.dodger import Dodger
from game_env.entities.enemies.tactical import Tactical
from game_env.entities.bosses.boss import Boss
from game_env.city import City



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
        self.enemy_bullets = []

        self.enemies = [
        ]

        self.boss = None
        self.stats = GameStats()
        self.hud = HUD()
        self.city = City()

        self.wave_manager = WaveManager(self)

        self.wave_manager.start_next_wave()


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
                if event.key == pygame.K_r:
                    self.restart()

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

        for bullet in self.enemy_bullets:
            bullet.update(dt)

        self.enemy_bullets = [
            bullet
            for bullet in self.enemy_bullets
            if bullet.rect.top < HEIGHT
        ]

        for bullet in self.bullets[:]:

            # boss collision
            if self.boss and bullet.rect.colliderect(
                self.boss.rect
            ):
                self.bullets.remove(bullet)

                self.boss.take_damage(1)

                self.stats.shots_hit += 1
                self.stats.score += 25

                if not self.boss.is_alive:
                    self.stats.kills += 1
                    self.stats.score += 1000
                    self.boss = None
                    self.stats.game_complete = True

                continue

            # enemy collision
            for enemy in self.enemies[:]:
                if bullet.rect.colliderect(enemy.rect):
                    self.bullets.remove(bullet)
                    self.enemies.remove(enemy)

                    self.stats.kills += 1
                    self.stats.shots_hit += 1
                    self.stats.score += 100

                    break

        for enemy in self.enemies[:]:
            enemy.update(dt, self)

            bullet = enemy.shoot()

            if bullet:
                self.enemy_bullets.append(bullet)

            if enemy.rect.colliderect(self.player.rect):
                self.stats.lives -= 1
                self.enemies.remove(enemy)

                if self.stats.lives <= 0:
                    self.game_over = True

                break

        for bullet in self.enemy_bullets[:]:
            if bullet.rect.colliderect(self.player.rect):
                self.enemy_bullets.remove(bullet)

                self.stats.lives -= 1

                if self.stats.lives <= 0:
                    self.game_over = True

                break

        if self.boss:
            self.boss.update(dt, self)

            bullet = self.boss.shoot()

            if bullet:
                self.enemy_bullets.append(bullet)

            if self.boss.rect.colliderect(
                self.player.rect
            ):
                self.stats.lives -= 1

                if self.stats.lives <= 0:
                    self.game_over = True

        self.wave_manager.update(dt)



    def draw(self):
        self.screen.fill(BACKGROUND_COLOR)

        self.city.draw(self.screen)

        self.player.draw(self.screen)

        for bullet in self.bullets:
            bullet.draw(self.screen)

        for enemy in self.enemies:
            enemy.draw(self.screen)

        if self.boss:
            self.boss.draw(self.screen)

        for bullet in self.enemy_bullets:
            bullet.draw(self.screen)

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


    def spawn_enemy(self, enemy_type, color, wave):
        margin = 100

        x = random.randint(
            margin,
            WIDTH - margin,
        )

        y = random.randint(
            50,
            HEIGHT // 3,
        )

        if enemy_type == "scout":
            enemy = Scout(
                x,
                y,
                color,
                wave,
            )

        elif enemy_type == "shooter":
            enemy = Shooter(
                x,
                y,
                color,
                wave,
            )

        elif enemy_type == "kamikaze":
            enemy = Kamikaze(
                x,
                y,
                color,
                wave,
            )


        elif enemy_type == "dodger":
            enemy = Dodger(
                x,
                y,
                color,
                wave,
            )

        elif enemy_type == "tactical":
            enemy = Tactical(
                x,
                y,
                color,
                wave,
            )

        else:
            return

        self.enemies.append(enemy)

    def restart(self):
        self.stats.reset()

        self.game_over = False

        self.player = Player()

        self.bullets = []
        self.enemies = []
        self.enemy_bullets = []
        self.boss = None

        self.wave_manager.current_wave = 0
        self.wave_manager.spawn_queue = []
        self.wave_manager.game_complete = False

        self.wave_manager.start_next_wave()