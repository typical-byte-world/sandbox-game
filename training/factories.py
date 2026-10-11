"""Construct experiment components without coupling agents to the runner."""

from pathlib import Path

import pygame

from agents.dqn_agent import DQNAgent
from agents.neural_agent import NeuralAgent
from game_env.config.learning import GAMMA
from game_env.controllers.random import RandomController
from game_env.core.simple_target import SimpleTargetEnv
from game_env.core.stagnation_space_invaders import StagnationSpaceInvadersEnv
from game_env.rendering.pygame_renderer import PygameRenderer
from training.trajectory_debugger import TrajectoryDebugger


def create_environment(
    environment, max_stagnation_steps, max_steps, reward_shaping, shaping_scale
):
    if environment == "simple-target":
        return SimpleTargetEnv(
            max_steps=max_steps,
            reward_shaping=reward_shaping,
            gamma=GAMMA,
            shaping_scale=shaping_scale,
        )
    return StagnationSpaceInvadersEnv(
        max_steps=max_steps, max_stagnation_steps=max_stagnation_steps
    )


def create_agent(agent_type, input_size, mode, model_path, n_steps, seed):
    if mode == "random":
        return RandomController()
    if agent_type == "dqn":
        agent = DQNAgent(
            input_size=input_size,
            training=mode == "train",
            n_steps=n_steps,
            gamma=GAMMA,
            seed=seed,
        )
    else:
        agent = NeuralAgent(input_size=input_size, training=mode == "train")
    if mode == "evaluate":
        if not model_path.exists():
            raise FileNotFoundError(f"Model not found: {model_path}")
        agent.load(model_path)
    return agent


def create_renderer(environment, render):
    if not render:
        return None
    if environment != "space-invaders":
        raise ValueError("Rendering is supported only for SpaceInvadersEnv")
    pygame.init()
    return PygameRenderer()


def create_debugger(agent_type, debug_last_steps, environment, experiment_name, mode):
    if not (
        environment == "space-invaders" and mode == "evaluate" and (agent_type == "dqn")
    ):
        return None
    return TrajectoryDebugger(
        output_dir=Path("results")
        / "space-invaders"
        / "dqn"
        / experiment_name
        / "stagnation",
        last_steps=debug_last_steps,
    )
