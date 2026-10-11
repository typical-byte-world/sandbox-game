"""Deterministic characterization captured before the structural refactor."""

import hashlib
import json
import random
import tempfile
from pathlib import Path

import numpy as np
import torch

from agents.dqn_agent import DQNAgent
from agents.neural_agent import NeuralAgent
from game_env.contracts.action import Action
from game_env.core.simple_target import SimpleTargetEnv
from game_env.core.space_invaders import SpaceInvadersEnv
from game_env.core.stagnation_space_invaders import StagnationSpaceInvadersEnv


def fingerprint():
    results = {}
    actions = Action.all_actions()
    for cls in (SimpleTargetEnv, SpaceInvadersEnv, StagnationSpaceInvadersEnv):
        for seed in (1, 42, 123):
            options = dict(max_steps=600)
            if cls is SimpleTargetEnv:
                options["reward_shaping"] = True
            env = cls(**options)
            state, info = env.reset(seed=seed)
            if cls is not SimpleTargetEnv:
                for enemy_type in ("shooter", "kamikaze", "dodger", "tactical"):
                    env.spawn_enemy(enemy_type, (100, 150, 200), 1)
            digest = hashlib.sha256()
            digest.update(state.tobytes())
            for step in range(600):
                state, reward, terminated, truncated, info = env.step(
                    actions[(step * 7 + step // 13) % 4]
                )
                digest.update(state.tobytes())
                digest.update(
                    json.dumps(
                        [reward, terminated, truncated, info], sort_keys=True
                    ).encode()
                )
                if terminated or truncated:
                    break
            results[f"{cls.__name__}/{seed}"] = digest.hexdigest()
    for cls in (NeuralAgent, DQNAgent):
        random.seed(42)
        np.random.seed(42)
        torch.manual_seed(42)
        options = dict(input_size=2)
        if cls is DQNAgent:
            options.update(
                batch_size=4,
                learning_starts=4,
                train_frequency=1,
                target_update_frequency=3,
                n_steps=3,
            )
        agent = cls(**options)
        digest = hashlib.sha256()
        for step in range(20):
            state = np.array([step / 20, 0.7], dtype=np.float32)
            next_state = np.array([(step + 1) / 20, 0.7], dtype=np.float32)
            action = agent.choose_action(state)
            digest.update(repr(action).encode())
            if cls is DQNAgent:
                agent.observe(state, action, 0.3, next_state, step == 19, False)
                network = agent.policy_network
            else:
                agent.update_q_values(state, action, 0.3, next_state, step == 19)
                network = agent.network
            for value in network.state_dict().values():
                digest.update(value.detach().numpy().tobytes())
        results[cls.__name__] = digest.hexdigest()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "model.pt"
            agent.save(path)
            restored = cls(**options)
            restored.load(path)
            restored_network = (
                restored.policy_network if cls is DQNAgent else restored.network
            )
            for key, value in network.state_dict().items():
                assert torch.equal(value, restored_network.state_dict()[key])
    return results
