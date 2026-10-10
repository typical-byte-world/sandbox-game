
import copy
import random

from game_env.core.environment import Environment
from game_env.controllers.action import Action

from game_env.settings import FPS, WIDTH, HEIGHT

from game_env.entities.player import Player
from game_env.entities.enemies.scout import Scout
from game_env.entities.enemies.shooter import Shooter
from game_env.entities.enemies.kamikaze import Kamikaze
from game_env.entities.enemies.dodger import Dodger
from game_env.entities.enemies.tactical import Tactical

from game_env.stats import GameStats
from game_env.wave_manager import WaveManager
from game_env.observations.continious import Observation
from game_env.agent.reward import Reward


class SpaceInvadersEnv(Environment):
    def __init__(self, max_steps=None):
        self.dt = 1.0 / FPS
        self.max_steps = max_steps

        self.observation = Observation()
        self.reward = Reward()

        self.wave_manager = WaveManager(self)

        self.player = None
        self.bullets = []
        self.enemy_bullets = []
        self.enemies = []
        self.boss = None

        self.stats = None
        self.game_over = False
        self.steps = 0

        self.reset()

    def reset(self, seed=None):
        if seed is not None:
            random.seed(seed)

        self.player = Player()

        self.bullets = []
        self.enemy_bullets = []
        self.enemies = []
        self.boss = None

        self.stats = GameStats()
        self.game_over = False
        self.steps = 0

        self.wave_manager.reset()

        observation = self.observation.get_vector(self)

        return observation, self._get_info()

    def step(self, action: Action):
        if self.game_over or self.stats.game_complete:
            raise RuntimeError(
                "Episode finished. Call reset() before step()."
            )

        if self.max_steps is not None:
            if self.steps >= self.max_steps:
                raise RuntimeError(
                    "Step limit reached. Call reset()."
                )

        self.steps += 1

        previous_stats = copy.deepcopy(self.stats)

        previous_x_player, previous_x_enemy = (
            self._get_aim_positions()
        )

        self._update_player(action)
        self._update_bullets()
        self._handle_player_bullet_collisions()
        self._update_enemies()
        self._update_enemy_bullets()
        self._update_boss()

        if not self.game_over and not self.stats.game_complete:
            self.wave_manager.update(self.dt)

        next_observation = self.observation.get_vector(self)

        current_x_player, current_x_enemy = (
            self._get_aim_positions()
        )

        reward = self.reward.calculate(
            previous_stats,
            self.stats,
            previous_x_player,
            previous_x_enemy,
            current_x_player,
            current_x_enemy,
        )

        terminated = (
            self.game_over
            or self.stats.game_complete
        )

        truncated = (
            self.max_steps is not None
            and self.steps >= self.max_steps
            and not terminated
        )

        return (
            next_observation,
            float(reward),
            terminated,
            truncated,
            self._get_info(),
        )

    def _get_info(self):
        return {
            "steps": self.steps,
            "wave": self.stats.wave,
            "lives": self.stats.lives,
            "kills": self.stats.kills,
            "shots_fired": self.stats.shots_fired,
            "shots_hit": self.stats.shots_hit,
            "score": self.stats.score,
            "survival_time": self.stats.survival_time,
            "game_complete": self.stats.game_complete,
        }

    def _get_closest_enemy(self):
        if not self.enemies:
            return None

        return min(
            self.enemies,
            key=lambda enemy: (
                enemy.position.distance_to(
                    self.player.position
                )
            ),
        )

    def _get_aim_positions(self):
        player_x = self.player.position.x

        closest_enemy = self._get_closest_enemy()

        if closest_enemy is None:
            return player_x, -1

        return player_x, closest_enemy.position.x

    def _update_player(self, action):
        self.player.apply_action(action)

        self.stats.survival_time += self.dt

        if action.shoot:
            bullet = self.player.shoot()

            if bullet:
                self.bullets.append(bullet)
                self.stats.shots_fired += 1

        self.player.update(self.dt)

    def _update_bullets(self):
        for bullet in self.bullets:
            bullet.update(self.dt)

        self.bullets = [
            bullet
            for bullet in self.bullets
            if bullet.rect.bottom > 0
        ]

        for bullet in self.enemy_bullets:
            bullet.update(self.dt)

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

    def _update_enemies(self):
        for enemy in self.enemies[:]:
            enemy.update(self.dt, self)

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

    def _update_boss(self):
        if not self.boss:
            return

        self.boss.update(self.dt, self)

        bullet = self.boss.shoot(self)

        if bullet:
            self.enemy_bullets.append(bullet)

        if self.boss.rect.colliderect(self.player.rect):
            self.stats.lives -= 1

            if self.stats.lives <= 0:
                self.game_over = True

    def spawn_enemy(self, enemy_type, color, wave):
        enemy_classes = {
            "scout": Scout,
            "shooter": Shooter,
            "kamikaze": Kamikaze,
            "dodger": Dodger,
            "tactical": Tactical,
        }

        enemy_class = enemy_classes.get(enemy_type)

        if enemy_class is None:
            raise ValueError(
                f"Unknown enemy type: {enemy_type}"
            )

        margin = 100

        x = random.randint(margin, WIDTH - margin)
        y = random.randint(50, HEIGHT // 3)

        enemy = enemy_class(
            x,
            y,
            color,
            wave,
        )

        self.enemies.append(enemy)
