
import csv
import random
from pathlib import Path
from statistics import mean

import numpy as np
import pygame
import torch

from game_env.agent.NeuralAgent import NeuralAgent
from game_env.controllers.random import RandomController
from game_env.core.simple_target import SimpleTargetEnv
from game_env.core.space_invaders import SpaceInvadersEnv
from game_env.rendering.pygame_renderer import PygameRenderer
from game_env.settings import FPS, GAMMA


class ExperimentRunner:
    COMMON_FIELDS = [
        "episode",
        "steps",
        "total_reward",
        "terminated",
        "truncated",
    ]

    SIMPLE_TARGET_FIELDS = [
        "success",
        "final_distance",
    ]

    SPACE_INVADERS_FIELDS = [
        "survival_time",
        "shots_fired",
        "shots_hit",
        "accuracy",
        "kills",
        "score",
        "lives_remaining",
        "game_complete",
    ]

    def __init__(
        self,
        mode="train",
        environment="space-invaders",
        episodes=20,
        max_steps=3600,
        seed=42,
        experiment_name="baseline",
        render=False,
        reward_shaping=False,
        shaping_scale=1.0,
    ):
        if mode not in ("train", "evaluate", "random"):
            raise ValueError(
                f"Unknown mode: {mode}"
            )

        if environment not in (
            "space-invaders",
            "simple-target",
        ):
            raise ValueError(
                f"Unknown environment: {environment}"
            )

        if episodes < 1:
            raise ValueError(
                "episodes must be >= 1"
            )

        if max_steps is not None and max_steps < 1:
            raise ValueError(
                "max_steps must be >= 1"
            )

        if render and environment != "space-invaders":
            raise ValueError(
                "Rendering is only supported for space-invaders."
            )

        if reward_shaping and environment != "simple-target":
            raise ValueError(
                "Reward shaping is only supported for simple-target."
            )

        if shaping_scale < 0:
            raise ValueError(
                "shaping_scale must be >= 0"
            )

        self.mode = mode
        self.environment_name = environment
        self.episodes = episodes
        self.max_steps = max_steps
        self.seed = seed
        self.experiment_name = experiment_name

        self.reward_shaping = reward_shaping
        self.shaping_scale = shaping_scale

        self.render_enabled = render
        self.renderer = None
        self.clock = None

        random.seed(seed)
        np.random.seed(seed)
        torch.manual_seed(seed)

        self.env = self._create_environment()

        observation, _ = self.env.reset(seed=seed)
        self.input_size = len(observation)

        self.model_path = (
            Path("models")
            / environment
            / f"{experiment_name}.pt"
        )

        self.results_path = (
            Path("results")
            / environment
            / f"{experiment_name}_{mode}.csv"
        )

        self.model_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.results_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.agent = self._create_agent()
        self.fields = self._get_fields()
        self.results = []

    def _create_environment(self):
        if self.environment_name == "simple-target":
            return SimpleTargetEnv(
                max_steps=self.max_steps,
                reward_shaping=self.reward_shaping,
                gamma=GAMMA,
                shaping_scale=self.shaping_scale,
            )

        return SpaceInvadersEnv(
            max_steps=self.max_steps
        )

    def _create_agent(self):
        if self.mode == "random":
            return RandomController()

        agent = NeuralAgent(
            input_size=self.input_size,
            training=self.mode == "train",
        )

        if self.mode == "evaluate":
            if not self.model_path.exists():
                raise FileNotFoundError(
                    f"Model not found: {self.model_path}"
                )

            agent.load(str(self.model_path))
            agent.network.eval()

        return agent

    def _get_fields(self):
        fields = self.COMMON_FIELDS.copy()

        if self.environment_name == "simple-target":
            fields.extend(self.SIMPLE_TARGET_FIELDS)
        else:
            fields.extend(self.SPACE_INVADERS_FIELDS)

        return fields

    def run(self):
        self.results = []
        self._initialize_csv()

        print(
            f"\nExperiment: {self.experiment_name}"
            f"\nEnvironment: {self.environment_name}"
            f"\nMode: {self.mode}"
            f"\nEpisodes: {self.episodes}"
            f"\nMax steps: {self.max_steps}"
            f"\nInput size: {self.input_size}"
            f"\nSeed: {self.seed}"
            f"\nRender: {self.render_enabled}"
            f"\nReward shaping: {self.reward_shaping}"
            f"\nShaping scale: {self.shaping_scale}\n"
        )

        completed = True

        try:
            if self.render_enabled:
                self.renderer = PygameRenderer()
                self.clock = pygame.time.Clock()

            for episode in range(1, self.episodes + 1):
                result = self._run_episode(episode)

                if result is None:
                    completed = False
                    break

                self.results.append(result)
                self._save_result(result)
                self._print_episode(result)

        finally:
            if self.renderer is not None:
                self.renderer.close()
                self.renderer = None
                self.clock = None

            if self.mode == "train":
                self.agent.save(str(self.model_path))
                print(f"\nModel saved: {self.model_path}")

        self._print_summary()

        if not completed:
            print("\nExperiment interrupted.")

        return self.results

    def _run_episode(self, episode):
        observation, info = self.env.reset(
            seed=self.seed + episode
        )

        total_reward = 0.0

        while True:
            if self.renderer is not None:
                if not self.renderer.handle_events():
                    return None

            action = self.agent.choose_action(observation)

            (
                next_observation,
                reward,
                terminated,
                truncated,
                info,
            ) = self.env.step(action)

            if self.mode == "train":
                self.agent.update_q_values(
                    observation,
                    action,
                    reward,
                    next_observation,
                    done=terminated,
                )

            total_reward += reward
            observation = next_observation

            if self.renderer is not None:
                self.renderer.render(
                    self.env,
                    self.agent,
                )
                self.clock.tick(FPS)

            if terminated or truncated:
                break

        result = {
            "episode": episode,
            "steps": info["steps"],
            "total_reward": round(total_reward, 6),
            "terminated": terminated,
            "truncated": truncated,
        }

        if self.environment_name == "simple-target":
            result.update({
                "success": info["success"],
                "final_distance": info["distance"],
            })

        else:
            shots_fired = info["shots_fired"]
            shots_hit = info["shots_hit"]

            accuracy = (
                shots_hit / shots_fired
                if shots_fired > 0
                else 0.0
            )

            result.update({
                "survival_time": round(
                    info["survival_time"], 3
                ),
                "shots_fired": shots_fired,
                "shots_hit": shots_hit,
                "accuracy": round(accuracy, 6),
                "kills": info["kills"],
                "score": info["score"],
                "lives_remaining": info["lives"],
                "game_complete": info["game_complete"],
            })

        return result

    def _initialize_csv(self):
        with self.results_path.open(
            "w",
            newline="",
            encoding="utf-8",
        ) as file:
            writer = csv.DictWriter(
                file,
                fieldnames=self.fields,
            )
            writer.writeheader()

    def _save_result(self, result):
        with self.results_path.open(
            "a",
            newline="",
            encoding="utf-8",
        ) as file:
            writer = csv.DictWriter(
                file,
                fieldnames=self.fields,
            )
            writer.writerow(result)

    def _print_episode(self, result):
        prefix = (
            f"Episode {result['episode']}/"
            f"{self.episodes} | "
            f"Steps: {result['steps']} | "
            f"Reward: {result['total_reward']:.2f}"
        )

        if self.environment_name == "simple-target":
            print(
                f"{prefix} | "
                f"Success: {result['success']} | "
                f"Distance: {result['final_distance']}"
            )
        else:
            print(
                f"{prefix} | "
                f"Kills: {result['kills']} | "
                f"Accuracy: {result['accuracy']:.2%}"
            )

    def _print_summary(self):
        if not self.results:
            print("\nNo completed episodes.")
            return

        print("\n" + "=" * 50)
        print("EXPERIMENT SUMMARY")
        print("=" * 50)

        print(f"Experiment: {self.experiment_name}")
        print(f"Environment: {self.environment_name}")
        print(f"Mode: {self.mode}")
        print(f"Completed episodes: {len(self.results)}")

        self._print_metric("steps")
        self._print_metric("total_reward")

        if self.environment_name == "simple-target":
            successes = sum(
                result["success"]
                for result in self.results
            )

            success_rate = successes / len(self.results)

            print(f"Success rate: {success_rate:.2%}")
            self._print_metric("final_distance")

        else:
            self._print_metric("survival_time")
            self._print_metric("kills")
            self._print_metric("shots_fired")
            self._print_metric("shots_hit")

            total_shots = sum(
                result["shots_fired"]
                for result in self.results
            )

            total_hits = sum(
                result["shots_hit"]
                for result in self.results
            )

            accuracy = (
                total_hits / total_shots
                if total_shots > 0
                else 0.0
            )

            print(f"Overall accuracy: {accuracy:.2%}")

            wins = sum(
                result["game_complete"]
                for result in self.results
            )

            print(f"Completed games: {wins}")

        terminated_count = sum(
            result["terminated"]
            for result in self.results
        )

        truncated_count = sum(
            result["truncated"]
            for result in self.results
        )

        print(f"Terminated: {terminated_count}")
        print(f"Truncated: {truncated_count}")
        print(f"Results: {self.results_path}")
        print("=" * 50)

    def _print_metric(self, metric):
        values = [
            result[metric]
            for result in self.results
        ]

        print(f"{metric}: {mean(values):.3f}")
