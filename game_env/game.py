import pygame
import random
import copy
import csv
import os
import numpy as np
from statistics import mean

from game_env.settings import (
    BACKGROUND_COLOR,
    FPS,
    HEIGHT,
    WIDTH,
)

from game_env.entities.player import Player
from game_env.stats import GameStats
from game_env.hud.hud import HUD
from game_env.entities.enemies.scout import Scout
from game_env.wave_manager import WaveManager
from game_env.entities.enemies.shooter import Shooter
from game_env.entities.enemies.kamikaze import Kamikaze
from game_env.entities.enemies.dodger import Dodger
from game_env.entities.enemies.tactical import Tactical
from game_env.city import City
from game_env.controllers.keyboard import KeyboardController
from game_env.controllers.random import RandomController
from game_env.observations.continious import Observation
from game_env.agent.agent import Agent
from game_env.agent.reward import Reward
from game_env.agent.NeuralAgent import NeuralAgent
from game_env.hud.ai_debug import AIDebug


EXPERIMENT_MODE = "random"  # train | evaluate | random

EXPERIMENT_EPISODES = 20

MODEL_PATH = "models/random_q_learning.npz"
EXPERIMENT_NAME = "random_q_learning"


FAST_TRAINING = True
RENDER = False

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
        self.action_counts = [0, 0, 0, 0]

        self.stats = GameStats()
        self.hud = HUD()
        self.city = City()
        self.wave_manager = WaveManager(self)

        # self.controller = KeyboardController()
        # self.controller = RandomController()
        # self.controller = Agent()


        if EXPERIMENT_MODE == "train":
            self.controller = NeuralAgent(training=True)

        elif EXPERIMENT_MODE == "evaluate":
            self.controller = NeuralAgent(training=False)
            self.controller.load(MODEL_PATH)

        elif EXPERIMENT_MODE == "random":
            self.controller = RandomController()

        else:
            raise ValueError(
                f"Unknown experiment mode: {EXPERIMENT_MODE}"
            )


        self.observation = Observation()
        self.reward = Reward()
        self.ai_debug = AIDebug()

        # Налаштування експерименту
        self.episode = 1
        self.experiment_episodes = EXPERIMENT_EPISODES
        self.completed_episodes = 0
        self.episode_reward = 0.0
        self.episode_steps = 0
        self.episode_start_steps = getattr(
            self.controller, "steps", 0
        )
        self.episode_results = []

        os.makedirs("results", exist_ok=True)
        self.results_file = (
            f"results/{EXPERIMENT_NAME}_{EXPERIMENT_MODE}.csv"
        )
        with open(
            self.results_file,
            "w",
            newline="",
            encoding="utf-8",
        ) as file:
            writer = csv.writer(file)
            writer.writerow([
                "episode",
                "steps",
                "survival_time",
                "shots_fired",
                "shots_hit",
                "accuracy",
                "kills",
                "score",
                "lives_remaining",
                "total_reward",
            ])

        self.wave_manager.start_next_wave()

    def run(self):
        while self.running:
            self.clock.tick(0)

            dt = 1.0 / FPS

            self.handle_events()

            if not self.running:
                break

            self.update(dt)

            if self.running and RENDER:
                self.draw()

        pygame.quit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    # Ручний рестарт не входить у статистику експерименту
                    self.restart()
                    self.episode_reward = 0.0
                    self.episode_start_steps = getattr(
                        self.controller, "steps", 0
                    )

    def update(self, dt):
        if self.game_over:
            self._finish_episode()
            return

        self.episode_steps += 1

        previous_stats = copy.deepcopy(self.stats)
        previous_x_player, previous_x_enemy = self._get_aim_positions()

        state = self.observation.get_vector(self)
        action = self.controller.choose_action(state)

        if EXPERIMENT_MODE == "evaluate":
            action_index = self.controller.actions.index(action)
            self.action_counts[action_index] += 1


        if (
            EXPERIMENT_MODE == "evaluate"
            and self.episode_steps % 100 == 0
        ):
            # q_values = self.controller.last_state_q_values
            q = self.controller.last_state_q_values

            print(
                f"\nStep: {self.episode_steps}",
                f"\nQ-values: {np.round(q, 4)}",
                f"\nBest action: {np.argmax(q)}",
                f"\nShoot Q: {q[3]:.4f}",
                f"\nBest Q: {np.max(q):.4f}",
                f"\nShoot gap: {np.max(q) - q[3]:.4f}",
            )
            # print(
            #     f"\nStep: {self.episode_steps}",
            #     f"\nQ-values: {np.round(q_values, 4)}",
            #     f"\nAction: {action}",
            # )


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

        self.episode_reward += reward

        if hasattr(self.controller, "update_q_values"):
            self.controller.update_q_values(
                state,
                action,
                reward,
                next_state,
                done=self.game_over,
            )

        if not FAST_TRAINING:
            self._debug_step(reward)


    def _finish_episode(self):
        self.completed_episodes += 1
        self.episode_steps = 0
        
        shots_fired = self.stats.shots_fired
        shots_hit = self.stats.shots_hit

        accuracy = (
            shots_hit / shots_fired
            if shots_fired > 0
            else 0.0
        )

        current_steps = getattr(self.controller, "steps", 0)
        steps = current_steps - self.episode_start_steps

        result = {
            "episode": self.completed_episodes,
            "steps": steps,
            "survival_time": round(self.stats.survival_time, 3),
            "shots_fired": shots_fired,
            "shots_hit": shots_hit,
            "accuracy": round(accuracy, 6),
            "kills": self.stats.kills,
            "score": self.stats.score,
            "lives_remaining": self.stats.lives,
            "total_reward": round(self.episode_reward, 6),
        }

        self.episode_results.append(result)

        with open(
            self.results_file,
            "a",
            newline="",
            encoding="utf-8",
        ) as file:
            writer = csv.DictWriter(
                file,
                fieldnames=result.keys(),
            )
            writer.writerow(result)

        print(
            f"[EPISODE {self.completed_episodes}/"
            f"{self.experiment_episodes}] "
            f"steps={steps} | "
            f"time={self.stats.survival_time:.1f}s | "
            f"hits={shots_hit} | "
            f"shots={shots_fired} | "
            f"accuracy={accuracy:.1%} | "
            f"kills={self.stats.kills} | "
            f"score={self.stats.score} | "
            f"reward={self.episode_reward:.3f}"
        )

        if self.completed_episodes >= self.experiment_episodes:
            if EXPERIMENT_MODE == "train":
                self.controller.save(MODEL_PATH)
                print(f"Model saved to: {MODEL_PATH}")

            self._print_experiment_summary()
            self.running = False
            return

        self.episode += 1
        self.restart()

        self.episode_reward = 0.0
        self.episode_start_steps = getattr(
            self.controller, "steps", 0
        )

    def _print_experiment_summary(self):
        results = self.episode_results

        if not results:
            print("No completed episodes.")
            return

        print("\n" + "=" * 55)
        print("EXPERIMENT SUMMARY")
        print("=" * 55)
        print(f"Completed episodes: {len(results)}")
        if EXPERIMENT_MODE == "evaluate":
            print("\nACTION DISTRIBUTION")

            total = sum(self.action_counts)

            for action, count in zip(
                self.controller.actions,
                self.action_counts,
            ):
                percentage = (
                    100 * count / total if total else 0
                )

                print(
                    f"{action}: {count} ({percentage:.2f}%)"
                )
        metrics = [
            ("steps", "Steps"),
            ("survival_time", "Survival time (s)"),
            ("shots_fired", "Shots fired"),
            ("shots_hit", "Hits"),
            ("kills", "Kills"),
            ("accuracy", "Accuracy"),
            ("total_reward", "Total reward"),
        ]

        for key, label in metrics:
            values = [row[key] for row in results]
            print(f"{label}: mean={mean(values):.3f}")

        first = results[:5]
        last = results[-5:]

        print("\nFirst 5 vs last 5 episodes:")

        for key, label in [
            ("survival_time", "Survival time"),
            ("shots_hit", "Hits"),
            ("kills", "Kills"),
            ("accuracy", "Accuracy"),
            ("total_reward", "Total reward"),
        ]:
            first_mean = mean(row[key] for row in first)
            last_mean = mean(row[key] for row in last)

            print(
                f"{label}: {first_mean:.3f} -> "
                f"{last_mean:.3f}"
            )

        print(f"\nCSV saved to: {self.results_file}")
        print("=" * 55)


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
            bullet for bullet in self.bullets
            if bullet.rect.bottom > 0
        ]

        for bullet in self.enemy_bullets:
            bullet.update(dt)

        self.enemy_bullets = [
            bullet for bullet in self.enemy_bullets
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

        bullet = self.boss.shoot(self)

        if bullet:
            self.enemy_bullets.append(bullet)

        if self.boss.rect.colliderect(self.player.rect):
            self.stats.lives -= 1

            if self.stats.lives <= 0:
                self.game_over = True

    def _debug_step(self, reward):
        if not hasattr(self.controller, "steps"):
            return

        if self.controller.steps % 200 != 0:
            return

        observation = self.observation.get_observation(self)

        print(
            "*******" * 10,
            "\n"
            "episode:", self.episode,
            "steps:", self.controller.steps,
            "*******" * 10,
            "\n"

        )

        print(
            "reward:", round(reward, 4),
            "shots_hit:", self.stats.shots_hit,
            "lives:", self.stats.lives,
            "game_complete:", self.stats.game_complete,
        )

        print(
            "player_x:", observation["player_x"],
            "player_y:", observation["player_y"],
            "player_bullet_present:",
            observation["player_bullet_present"],
            "player_bullet_dx:",
            observation["player_bullet_dx"],
            "player_bullet_dy:",
            observation["player_bullet_dy"],
            "enemy_present:", observation["enemy_present"],
            "enemy_dx:", observation["enemy_dx"],
            "enemy_dy:", observation["enemy_dy"],
            "enemy_bullet_present:",
            observation["enemy_bullet_present"],
            "enemy_bullet_dx:",
            observation["enemy_bullet_dx"],
            "enemy_bullet_dy:",
            observation["enemy_bullet_dy"],
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
            self.hud.draw_game_over(self.screen, self.stats)
        else:
            self.hud.draw(self.screen, self.stats)

        if isinstance(self.controller, NeuralAgent):
            self.ai_debug.draw(self.screen, self.controller)

        pygame.display.flip()

    def spawn_enemy(self, enemy_type, color, wave):
        margin = 100

        x = random.randint(margin, WIDTH - margin)
        y = random.randint(50, HEIGHT // 3)

        if enemy_type == "scout":
            enemy = Scout(x, y, color, wave)
        elif enemy_type == "shooter":
            enemy = Shooter(x, y, color, wave)
        elif enemy_type == "kamikaze":
            enemy = Kamikaze(x, y, color, wave)
        elif enemy_type == "dodger":
            enemy = Dodger(x, y, color, wave)
        elif enemy_type == "tactical":
            enemy = Tactical(x, y, color, wave)
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