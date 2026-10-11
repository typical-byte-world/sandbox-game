"""Characterize boundary rules and rendering with the original implementation."""

import hashlib
import json
import os
import random

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

import pygame

from game_env.contracts.action import Action
from game_env.core.space_invaders import SpaceInvadersEnv
from game_env.entities.bosses.boss import Boss
from game_env.entities.enemies.dodger import Dodger
from game_env.entities.enemies.kamikaze import Kamikaze
from game_env.entities.enemies.scout import Scout
from game_env.entities.enemies.shooter import Shooter
from game_env.entities.enemies.tactical import Tactical
from game_env.rendering.pygame_renderer import PygameRenderer


def rendering_fingerprint():
    results = {}
    for cls in (Scout, Shooter, Kamikaze, Dodger, Tactical, Boss):
        values = []
        for x, y in ((-100, -100), (1800, 1200), (800, 500)):
            entity = cls(x, y) if cls is Boss else cls(x, y, (100, 150, 200), 1)
            entity.velocity = pygame.Vector2(30, -50)
            entity.handle_screen_collision()
            values.append([list(entity.position), list(entity.velocity)])
        results[cls.__name__] = values
    env = SpaceInvadersEnv(max_steps=100)
    env.reset(seed=42)
    for enemy_type in ("shooter", "kamikaze", "dodger", "tactical"):
        env.spawn_enemy(enemy_type, (100, 150, 200), 1)
    env.boss = Boss(800, 250)
    random.seed(42)
    renderer = PygameRenderer()
    try:
        digest = hashlib.sha256()
        for step in range(20):
            state, reward, terminated, truncated, info = env.step(
                Action.all_actions()[step % 4]
            )
            renderer.render(env)
            digest.update(pygame.image.tobytes(renderer.screen, "RGB"))
            digest.update(state.tobytes())
            digest.update(
                json.dumps(
                    [reward, terminated, truncated, info], sort_keys=True
                ).encode()
            )
        results["frames_and_boss"] = digest.hexdigest()
    finally:
        renderer.close()
    return results
