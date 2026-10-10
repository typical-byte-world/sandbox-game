
import random

import numpy as np

from game_env.core.environment import Environment
from game_env.controllers.action import Action


class SimpleTargetEnv(Environment):
    def __init__(
        self,
        width=100,
        move_speed=5,
        hit_radius=5,
        max_steps=600,
        reward_shaping=False,
        gamma=0.99,
        shaping_scale=1.0,
    ):
        self.width = width
        self.move_speed = move_speed
        self.hit_radius = hit_radius
        self.max_steps = max_steps

        self.reward_shaping = reward_shaping
        self.gamma = gamma
        self.shaping_scale = shaping_scale

        self.rng = random.Random()

        self.player_x = 0
        self.target_x = 0
        self.steps = 0

        self.terminated = False
        self.truncated = False

        self.reset()

    def reset(self, seed=None):
        if seed is not None:
            self.rng.seed(seed)

        self.player_x = self.rng.randint(
            0, self.width
        )

        self.target_x = self.rng.randint(
            0, self.width
        )

        self.steps = 0
        self.terminated = False
        self.truncated = False

        return (
            self._get_observation(),
            self._get_info(),
        )

    def step(self, action: Action):
        if self.terminated or self.truncated:
            raise RuntimeError(
                "Episode finished. Call reset()."
            )

        previous_potential = self._potential()

        self.steps += 1

        # 1. Movement
        self.player_x += (
            action.move_x * self.move_speed
        )

        self.player_x = max(
            0,
            min(self.width, self.player_x),
        )

        # 2. Original reward
        reward = -0.01

        hit = (
            action.shoot
            and abs(self.player_x - self.target_x)
            <= self.hit_radius
        )

        if hit:
            reward += 10.0
            self.terminated = True

        if (
            self.steps >= self.max_steps
            and not self.terminated
        ):
            self.truncated = True

        # 3. Potential-based reward shaping
        if self.reward_shaping:
            if self.terminated:
                next_potential = 0.0
            else:
                next_potential = self._potential()

            shaping_reward = self.shaping_scale * (
                self.gamma * next_potential
                - previous_potential
            )

            reward += shaping_reward

        return (
            self._get_observation(),
            float(reward),
            self.terminated,
            self.truncated,
            self._get_info(),
        )

    def _potential(self):
        distance = abs(
            self.player_x - self.target_x
        )

        return -distance / self.width

    def _get_observation(self):
        return np.array(
            [
                self.player_x / self.width,
                self.target_x / self.width,
            ],
            dtype=np.float32,
        )

    def _get_info(self):
        return {
            "steps": self.steps,
            "player_x": self.player_x,
            "target_x": self.target_x,
            "distance": abs(
                self.player_x - self.target_x
            ),
            "success": self.terminated,
        }
