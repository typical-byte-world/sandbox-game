
from dataclasses import dataclass

import numpy as np

from game_env.settings import (
    WIDTH,
    HEIGHT,
    PLAYER_MAX_SPEED,
    PLAYER_ACCELERATION,
    BOSS_MAX_SPEED,
    BOSS_DASH_SPEED,
    BOSS_ACCELERATION,
    ENEMY_BULLET_SPEED,
    BULLET_SPEED,
    SCOUT_MAX_SPEED,
    SHOOTER_MAX_SPEED,
    KAMIKAZE_MAX_SPEED,
    DODGER_MAX_SPEED,
    TACTICAL_MAX_SPEED,
)

from game_env.entities.enemies.scout import Scout
from game_env.entities.enemies.shooter import Shooter
from game_env.entities.enemies.kamikaze import Kamikaze
from game_env.entities.enemies.dodger import Dodger
from game_env.entities.enemies.tactical import Tactical


@dataclass(frozen=True)
class ObservationConfig:
    max_enemies: int = 20
    max_player_bullets: int = 30
    max_enemy_bullets: int = 30

    max_lives: int = 3
    max_waves: int = 1

    max_episode_steps: int = 3600


class FullStateObservation:
    PLAYER_FEATURES = 10
    ENEMY_FEATURES = 14
    BULLET_FEATURES = 9
    BOSS_FEATURES = 10
    GLOBAL_FEATURES = 4

    ENEMY_TYPES = (
        Scout,
        Shooter,
        Kamikaze,
        Dodger,
        Tactical,
    )

    def __init__(self, config=None):
        self.config = config or ObservationConfig()

        self.max_enemy_speed = max(
            SCOUT_MAX_SPEED,
            SHOOTER_MAX_SPEED,
            KAMIKAZE_MAX_SPEED * 1.5,
            DODGER_MAX_SPEED,
            TACTICAL_MAX_SPEED,
        ) * 2.0

        self.max_boss_speed = max(
            BOSS_MAX_SPEED,
            BOSS_DASH_SPEED,
        )

        self.input_size = (
            self.PLAYER_FEATURES
            + self.config.max_enemies * self.ENEMY_FEATURES
            + self.config.max_player_bullets * self.BULLET_FEATURES
            + self.config.max_enemy_bullets * self.BULLET_FEATURES
            + self.BOSS_FEATURES
            + self.GLOBAL_FEATURES
        )

    def get_vector(self, env):
        features = []

        features.extend(
            self._encode_player(env)
        )

        features.extend(
            self._encode_collection(
                env.enemies,
                self.config.max_enemies,
                self.ENEMY_FEATURES,
                lambda enemy: self._encode_enemy(
                    enemy,
                    env.player,
                ),
            )
        )

        features.extend(
            self._encode_collection(
                env.bullets,
                self.config.max_player_bullets,
                self.BULLET_FEATURES,
                lambda bullet: self._encode_bullet(
                    bullet,
                    env.player,
                    BULLET_SPEED,
                ),
            )
        )

        features.extend(
            self._encode_collection(
                env.enemy_bullets,
                self.config.max_enemy_bullets,
                self.BULLET_FEATURES,
                lambda bullet: self._encode_bullet(
                    bullet,
                    env.player,
                    ENEMY_BULLET_SPEED,
                ),
            )
        )

        features.extend(
            self._encode_boss(
                env.boss,
                env.player,
            )
        )

        features.extend(
            self._encode_global(env)
        )

        vector = np.asarray(
            features,
            dtype=np.float32,
        )

        if vector.shape != (self.input_size,):
            raise ValueError(
                f"Invalid observation shape: {vector.shape}. "
                f"Expected ({self.input_size},)"
            )

        if not np.all(np.isfinite(vector)):
            raise ValueError(
                "Observation contains NaN or infinity."
            )

        return vector

    def _encode_player(self, env):
        player = env.player

        return [
            player.position.x / WIDTH,
            player.position.y / HEIGHT,

            player.velocity.x / PLAYER_MAX_SPEED,
            player.velocity.y / PLAYER_MAX_SPEED,

            player.acceleration.x / PLAYER_ACCELERATION,
            player.acceleration.y / PLAYER_ACCELERATION,

            player.rect.width / WIDTH,
            player.rect.height / HEIGHT,

            player.shoot_cooldown / player.shoot_delay,

            env.stats.lives / self.config.max_lives,
        ]

    def _encode_enemy(self, enemy, player):
        enemy_type = [
            float(isinstance(enemy, cls))
            for cls in self.ENEMY_TYPES
        ]

        return [
            1.0,

            enemy.position.x / WIDTH,
            enemy.position.y / HEIGHT,

            (enemy.position.x - player.position.x) / WIDTH,
            (enemy.position.y - player.position.y) / HEIGHT,

            enemy.rect.width / WIDTH,
            enemy.rect.height / HEIGHT,

            enemy.velocity.x / self.max_enemy_speed,
            enemy.velocity.y / self.max_enemy_speed,

            *enemy_type,
        ]

    def _encode_bullet(
        self,
        bullet,
        player,
        max_speed,
    ):
        return [
            1.0,

            bullet.position.x / WIDTH,
            bullet.position.y / HEIGHT,

            (bullet.position.x - player.position.x) / WIDTH,
            (bullet.position.y - player.position.y) / HEIGHT,

            bullet.rect.width / WIDTH,
            bullet.rect.height / HEIGHT,

            bullet.velocity.x / max_speed,
            bullet.velocity.y / max_speed,
        ]

    def _encode_boss(self, boss, player):
        if boss is None:
            return [0.0] * self.BOSS_FEATURES

        return [
            1.0,

            boss.position.x / WIDTH,
            boss.position.y / HEIGHT,

            (boss.position.x - player.position.x) / WIDTH,
            (boss.position.y - player.position.y) / HEIGHT,

            boss.rect.width / WIDTH,
            boss.rect.height / HEIGHT,

            boss.velocity.x / self.max_boss_speed,
            boss.velocity.y / self.max_boss_speed,

            boss.health / boss.max_health,
        ]

    def _encode_global(self, env):
        return [
            env.stats.wave / self.config.max_waves,

            len(env.enemies) / self.config.max_enemies,

            len(env.enemy_bullets)
            / self.config.max_enemy_bullets,

            env.steps / self.config.max_episode_steps,
        ]

    def _encode_collection(
        self,
        objects,
        max_count,
        feature_count,
        encoder,
    ):
        if len(objects) > max_count:
            raise ValueError(
                f"Object limit exceeded: "
                f"{len(objects)} > {max_count}"
            )

        ordered = sorted(
            objects,
            key=lambda obj: (
                obj.position.x,
                obj.position.y,
            ),
        )

        features = []

        for obj in ordered:
            encoded = encoder(obj)

            if len(encoded) != feature_count:
                raise ValueError(
                    f"Expected {feature_count} features, "
                    f"got {len(encoded)}."
                )

            features.extend(encoded)

        missing = max_count - len(ordered)

        features.extend(
            [0.0] * (missing * feature_count)
        )

        return features
