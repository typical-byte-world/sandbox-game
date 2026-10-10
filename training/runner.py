
import csv
import random
from pathlib import Path
from statistics import mean

import numpy as np
import pygame

from game_env.settings import FPS
from game_env.agent.NeuralAgent import NeuralAgent
from game_env.controllers.random import RandomController
from game_env.core.space_invaders import SpaceInvadersEnv
from game_env.rendering.pygame_renderer import PygameRenderer


class ExperimentRunner:
    FIELDS = [
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
        "terminated",
        "truncated",
    ]

    def __init__(
        self,
        mode="train",
        episodes=20,
        max_steps=3600,
        seed=42,
        experiment_name="baseline",
        render=False,
    ):
        if mode not in ("train", "evaluate", "random"):
            raise ValueError(f"Unknown mode: {mode}")

        if episodes < 1:
            raise ValueError("episodes must be >= 1")

        if max_steps is not None and max_steps < 1:
            raise ValueError("max_steps must be >= 1")

        self.mode = mode
        self.episodes = episodes
        self.seed = seed
        self.experiment_name = experiment_name

        self.render_enabled = render
        self.renderer = None
        self.clock = None

        random.seed(seed)
        np.random.seed(seed)

        self.env = SpaceInvadersEnv(
            max_steps=max_steps
        )

        self.model_path = Path(
            f"models/{experiment_name}.npz"
        )

        self.results_path = Path(
            f"results/{experiment_name}_{mode}.csv"
        )

        self.results_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.agent = self._create_agent()
        self.results = []

    def _create_agent(self):
        if self.mode == "random":
            return RandomController()

        agent = NeuralAgent(
            training=self.mode == "train"
        )

        if self.mode == "evaluate":
            agent.load(str(self.model_path))

        return agent

    def run(self):
        self.results = []
        self._initialize_csv()

        print(
            f"\nExperiment: {self.experiment_name}"
            f"\nMode: {self.mode}"
            f"\nEpisodes: {self.episodes}"
            f"\nSeed: {self.seed}"
            f"\nRender: {self.render_enabled}\n"
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
                print(
                    f"\nModel saved: {self.model_path}"
                )

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

            action = self.agent.choose_action(
                observation
            )

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

        shots_fired = info["shots_fired"]
        shots_hit = info["shots_hit"]

        accuracy = (
            shots_hit / shots_fired
            if shots_fired > 0
            else 0.0
        )

        return {
            "episode": episode,
            "steps": info["steps"],
            "survival_time": round(
                info["survival_time"], 3
            ),
            "shots_fired": shots_fired,
            "shots_hit": shots_hit,
            "accuracy": round(accuracy, 6),
            "kills": info["kills"],
            "score": info["score"],
            "lives_remaining": info["lives"],
            "total_reward": round(
                total_reward, 6
            ),
            "terminated": terminated,
            "truncated": truncated,
        }

    def _initialize_csv(self):
        with self.results_path.open(
            "w",
            newline="",
            encoding="utf-8",
        ) as file:
            writer = csv.DictWriter(
                file,
                fieldnames=self.FIELDS,
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
                fieldnames=self.FIELDS,
            )
            writer.writerow(result)

    def _print_episode(self, result):
        print(
            f"Episode {result['episode']}/"
            f"{self.episodes} | "
            f"Steps: {result['steps']} | "
            f"Kills: {result['kills']} | "
            f"Accuracy: {result['accuracy']:.2%} | "
            f"Reward: {result['total_reward']:.2f} | "
            f"Terminated: {result['terminated']} | "
            f"Truncated: {result['truncated']}"
        )

    def _print_summary(self):
        if not self.results:
            print("\nNo completed episodes.")
            return

        print("\n" + "=" * 50)
        print("EXPERIMENT SUMMARY")
        print("=" * 50)

        print(f"Experiment: {self.experiment_name}")
        print(f"Mode: {self.mode}")
        print(f"Completed episodes: {len(self.results)}")

        metrics = (
            "steps",
            "survival_time",
            "shots_fired",
            "shots_hit",
            "kills",
            "total_reward",
        )

        for metric in metrics:
            values = [
                result[metric]
                for result in self.results
            ]

            print(
                f"{metric}: {mean(values):.3f}"
            )

        total_shots = sum(
            result["shots_fired"]
            for result in self.results
        )

        total_hits = sum(
            result["shots_hit"]
            for result in self.results
        )

        overall_accuracy = (
            total_hits / total_shots
            if total_shots > 0
            else 0.0
        )

        print(
            f"Overall accuracy: {overall_accuracy:.2%}"
        )

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
