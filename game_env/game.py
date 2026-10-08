import pygame
import random
import copy

from game_env.settings import (
    BACKGROUND_COLOR,
    FPS,
    HEIGHT,
    WIDTH,
    ZONES
)

from game_env.entities.player import Player
from game_env.entities.enemy import Enemy
from game_env.stats import GameStats
from game_env.hud.hud import HUD
from game_env.entities.enemies.scout import Scout
from game_env.wave_manager import WaveManager
from game_env.entities.enemies.shooter import Shooter
from game_env.entities.enemies.kamikaze import Kamikaze
from game_env.entities.enemies.dodger import Dodger
from game_env.entities.enemies.tactical import Tactical
from game_env.entities.bosses.boss import Boss
from game_env.city import City
from game_env.controllers.keyboard import KeyboardController
from game_env.controllers.random import RandomController
# from game_env.observations.discrete import Observation
from game_env.observations.continious import Observation
from game_env.agent.agent import Agent
from game_env.agent.reward import Reward
from game_env.agent.NeuralAgent import NeuralAgent


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
        self.enemies = []

        self.boss = None

        self.stats = GameStats()
        self.hud = HUD()
        self.city = City()

        self.wave_manager = WaveManager(self)

        # self.controller = KeyboardController()
        # self.controller = RandomController()
        # self.controller = Agent()
        self.controller = NeuralAgent()

        self.observation = Observation()

        self.reward = Reward()

        self.episode = 1

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

    
    def update(self, dt):
        if self.game_over:
            self.episode += 1
            self.restart()
            return

        previous_stats = copy.deepcopy(self.stats)
        previous_x_player, previous_x_enemy = self._get_aim_positions()

        state = self.observation.get_vector(self)
        action = self.controller.choose_action(state)

        self._update_player(action, dt)
        self._update_bullets(dt)
        self._handle_player_bullet_collisions()
        self._update_enemies(dt)
        self._update_enemy_bullets()
        self._update_boss(dt)

        self.wave_manager.update(dt)

        next_state = self.observation.get_vector(self)
        current_x_player, current_x_enemy = self._get_aim_positions()

        reward = self.reward.calculate(
            previous_stats,
            self.stats,
            previous_x_player,
            previous_x_enemy,
            current_x_player,
            current_x_enemy,
        )

        self.controller.update_q_values(
            state,
            action,
            reward,
            next_state,
        )

        self._debug_step(reward)


    def _get_closest_enemy(self):
        if not self.enemies:
            return None

        return min(
            self.enemies,
            key=lambda enemy: enemy.position.distance_to(
                self.player.position
            ),
        )


    def _get_aim_positions(self):
        player_x = self.player.position.x
        closest_enemy = self._get_closest_enemy()

        if closest_enemy is None:
            return player_x, -1

        return player_x, closest_enemy.position.x


    def _update_player(self, action, dt):
        self.player.apply_action(action)

        self.stats.survival_time += dt

        if action.shoot:
            bullet = self.player.shoot()

            if bullet:
                self.bullets.append(bullet)
                self.stats.shots_fired += 1

        self.player.update(dt)


    def _update_bullets(self, dt):
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


    def _handle_player_bullet_collisions(self):
        for bullet in self.bullets[:]:
            if self._handle_boss_bullet_collision(bullet):
                continue

            self._handle_enemy_bullet_collision(bullet)


    def _handle_boss_bullet_collision(self, bullet):
        if not self.boss:
            return False

        if not bullet.rect.colliderect(self.boss.rect):
            return False

        self.bullets.remove(bullet)

        self.boss.take_damage(1)

        self.stats.shots_hit += 1
        self.stats.score += 25

        if not self.boss.is_alive:
            self.stats.kills += 1
            self.stats.score += 1000
            self.boss = None
            self.stats.game_complete = True

        return True


    def _handle_enemy_bullet_collision(self, bullet):
        for enemy in self.enemies[:]:
            if not bullet.rect.colliderect(enemy.rect):
                continue

            self.bullets.remove(bullet)
            self.enemies.remove(enemy)

            self.stats.kills += 1
            self.stats.shots_hit += 1
            self.stats.score += 100

            return True

        return False


    def _update_enemies(self, dt):
        for enemy in self.enemies[:]:
            enemy.update(dt, self)

            if isinstance(enemy, Shooter):
                bullet = enemy.shoot(self.player.position)

                if bullet:
                    self.enemy_bullets.append(bullet)

            if enemy.rect.colliderect(self.player.rect):
                self.stats.lives -= 1
                self.enemies.remove(enemy)

                if self.stats.lives <= 0:
                    self.game_over = True

                break


    def _update_enemy_bullets(self):
        for bullet in self.enemy_bullets[:]:
            if not bullet.rect.colliderect(self.player.rect):
                continue

            self.enemy_bullets.remove(bullet)

            self.stats.lives -= 1

            if self.stats.lives <= 0:
                self.game_over = True

            break


    def _update_boss(self, dt):
        if not self.boss:
            return

        self.boss.update(dt, self)

        bullet = self.boss.shoot()

        if bullet:
            self.enemy_bullets.append(bullet)

        if self.boss.rect.colliderect(self.player.rect):
            self.stats.lives -= 1

            if self.stats.lives <= 0:
                self.game_over = True


    def _debug_step(self, reward):

        if self.controller.steps % 200 != 0:
            return

        observation = self.observation.get_observation(self)
        

        print(
            "episode:", self.episode,
            "steps:", self.controller.steps,
        )

        print(
            "shots_hit:", self.stats.shots_hit,
            "lives:", self.stats.lives,
            "game_complete:", self.stats.game_complete,
        )

        print(
            'player_x', observation['player_x'],
            'player_y', observation['player_y'],

            'player_bullet_present', observation['player_bullet_present'],
            'player_bullet_dx', observation['player_bullet_dx'],
            'player_bullet_dy', observation['player_bullet_dy'],

            'enemy_present', observation['enemy_present'],
            'enemy_dx', observation['enemy_dx'],
            'enemy_dy', observation['enemy_dy'],


            'enemy_bullet_present', observation['enemy_bullet_present'],
            'enemy_bullet_dx', observation['enemy_bullet_dx'],
            'enemy_bullet_dy', observation['enemy_bullet_dy'],
            '---' * 10
        )

        print(self.observation.get_vector(self))


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

        # self.draw_state_grid()

        pygame.display.flip()

    # def draw_state_grid(self):
    #     cell_width = WIDTH / ZONES
    #     cell_height = HEIGHT / ZONES

    #     color = (60, 60, 60)

    #     for column in range(ZONES + 1):
    #         x = column * cell_width

    #         pygame.draw.line(
    #             self.screen,
    #             color,
    #             (x, 0),
    #             (x, HEIGHT),
    #         )

    #     for row in range(ZONES + 1):
    #         y = row * cell_height

    #         pygame.draw.line(
    #             self.screen,
    #             color,
    #             (0, y),
    #             (WIDTH, y),
    #         )

    #     # player_x, player_y, enemy_x, enemy_y, enemy_bullet_x, enemy_bullet_y, bullet_x, bullet_y = (
    #     #     self.observation.get_state(self)
    #     # )

    #     player_rect = pygame.Rect(
    #         player_x * cell_width,
    #         player_y * cell_height,
    #         cell_width,
    #         cell_height,
    #     )

    #     pygame.draw.rect(
    #         self.screen,
    #         (50, 100, 255),
    #         player_rect,
    #         3,
    #     )

    #     if enemy_x != -1:
    #         enemy_rect = pygame.Rect(
    #             enemy_x * cell_width,
    #             enemy_y * cell_height,
    #             cell_width,
    #             cell_height,
    #         )

    #         pygame.draw.rect(
    #             self.screen,
    #             (255, 60, 60),
    #             enemy_rect,
    #             3,
    #         )

    #     if enemy_bullet_x != -1:
    #         bullet_rect = pygame.Rect(
    #             enemy_bullet_x * cell_width,
    #             enemy_bullet_y * cell_height,
    #             cell_width,
    #             cell_height,
    #         )

    #         pygame.draw.rect(
    #             self.screen,
    #             (255, 220, 50),
    #             bullet_rect,
    #             3,
    #         )
            


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