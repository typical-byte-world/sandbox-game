
import csv
import random
from pathlib import Path
from statistics import mean

import numpy as np
import pygame
import torch

from game_env.agent.NeuralAgent import NeuralAgent
from game_env.agent.dqn_agent import DQNAgent
from game_env.controllers.random import RandomController
from game_env.core.simple_target import SimpleTargetEnv
from game_env.core.stagnation_space_invaders import (
    StagnationSpaceInvadersEnv,
)
from game_env.rendering.pygame_renderer import PygameRenderer
from game_env.settings import FPS, GAMMA
from training.trajectory_debugger import TrajectoryDebugger


class ExperimentRunner:
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
        agent_type="neural",
        n_steps=5,
        max_stagnation_steps=300,
        debug_last_steps=30,
    ):
        if mode not in {"train", "evaluate", "random"}:
            raise ValueError(f"Unknown mode: {mode}")

        if environment not in {
            "space-invaders",
            "simple-target",
        }:
            raise ValueError(
                f"Unknown environment: {environment}"
            )

        if agent_type not in {"neural", "dqn"}:
            raise ValueError(
                f"Unknown agent type: {agent_type}"
            )

        if episodes < 1:
            raise ValueError("episodes must be >= 1")

        if max_steps < 1:
            raise ValueError("max_steps must be >= 1")

        if n_steps < 1:
            raise ValueError("n_steps must be >= 1")

        if (
            max_stagnation_steps is not None
            and max_stagnation_steps < 1
        ):
            raise ValueError(
                "max_stagnation_steps must be >= 1"
            )

        if debug_last_steps < 1:
            raise ValueError(
                "debug_last_steps must be >= 1"
            )

        self.mode = mode
        self.environment = environment
        self.episodes = episodes
        self.max_steps = max_steps
        self.seed = seed
        self.experiment_name = experiment_name
        self.render = render

        self.reward_shaping = reward_shaping
        self.shaping_scale = shaping_scale

        self.agent_type = agent_type
        self.n_steps = n_steps

        self.max_stagnation_steps = (
            max_stagnation_steps
        )
        self.debug_last_steps = debug_last_steps

        random.seed(seed)
        np.random.seed(seed)
        torch.manual_seed(seed)

        self.env = self._create_environment()

        observation, _ = self.env.reset(seed=seed)
        self.input_size = len(observation)

        if self.agent_type == "dqn":
            self.model_path = (
                Path("models")
                / environment
                / "dqn"
                / f"{experiment_name}.pt"
            )

            self.results_path = (
                Path("results")
                / environment
                / "dqn"
                / f"{experiment_name}_{mode}.csv"
            )

        else:
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

    def _create_environment(self):
        if self.environment == "simple-target":
            return SimpleTargetEnv(
                max_steps=self.max_steps,
                reward_shaping=self.reward_shaping,
                gamma=GAMMA,
                shaping_scale=self.shaping_scale,
            )

        return StagnationSpaceInvadersEnv(
            max_steps=self.max_steps,
            max_stagnation_steps=(
                self.max_stagnation_steps
            ),
        )

    def _create_agent(self):
        if self.mode == "random":
            return RandomController()

        if self.agent_type == "dqn":
            agent = DQNAgent(
                input_size=self.input_size,
                training=self.mode == "train",
                n_steps=self.n_steps,
                gamma=GAMMA,
                seed=self.seed,
            )

            if self.mode == "evaluate":
                if not self.model_path.exists():
                    raise FileNotFoundError(
                        f"Model not found: {self.model_path}"
                    )

                agent.load(self.model_path)

            return agent

        agent = NeuralAgent(
            input_size=self.input_size,
            training=self.mode == "train",
        )

        if self.mode == "evaluate":
            if not self.model_path.exists():
                raise FileNotFoundError(
                    f"Model not found: {self.model_path}"
                )

            agent.load(self.model_path)

        return agent

    def _create_renderer(self):
        if not self.render:
            return None

        if self.environment != "space-invaders":
            raise ValueError(
                "Rendering is supported only "
                "for SpaceInvadersEnv"
            )

        pygame.init()

        return PygameRenderer()

    def _create_debugger(self):
        if not (
            self.environment == "space-invaders"
            and self.mode == "evaluate"
            and self.agent_type == "dqn"
        ):
            return None

        return TrajectoryDebugger(
            output_dir=(
                Path("results")
                / "space-invaders"
                / "dqn"
                / self.experiment_name
                / "stagnation"
            ),
            last_steps=self.debug_last_steps,
        )

    def _choose_action(self, agent, observation):
        return agent.choose_action(observation)

    def _train_agent(
        self,
        agent,
        observation,
        action,
        reward,
        next_observation,
        terminated,
        truncated,
    ):
        if self.mode != "train":
            return

        if isinstance(agent, DQNAgent):
            agent.observe(
                state=observation,
                action=action,
                reward=reward,
                next_state=next_observation,
                terminated=terminated,
                truncated=truncated,
            )
            return

        agent.update_q_values(
            state=observation,
            action=action,
            reward=reward,
            next_state=next_observation,
            done=terminated,
        )

    def _handle_render(self, renderer, agent):
        if renderer is None:
            return True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

        renderer.render(self.env, agent)
        return True

    def _make_result(
        self,
        episode,
        steps,
        total_reward,
        terminated,
        truncated,
        info,
    ):
        result = {
            "episode": episode,
            "seed": self.seed + episode,
            "steps": steps,
            "total_reward": total_reward,
            "terminated": terminated,
            "truncated": truncated,
        }

        if self.environment == "simple-target":
            result.update({
                "success": bool(
                    info.get("success", False)
                ),
                "final_distance": info.get(
                    "distance",
                    info.get("final_distance"),
                ),
            })

        else:
            shots_fired = info.get("shots_fired", 0)
            shots_hit = info.get("shots_hit", 0)

            accuracy = (
                shots_hit / shots_fired
                if shots_fired > 0
                else 0.0
            )

            result.update({
                "wave": info.get("wave", 0),
                "survival_time": info.get(
                    "survival_time", 0.0
                ),
                "shots_fired": shots_fired,
                "shots_hit": shots_hit,
                "accuracy": accuracy,
                "kills": info.get("kills", 0),
                "score": info.get("score", 0),
                "lives_remaining": info.get(
                    "lives", 0
                ),
                "game_complete": info.get(
                    "game_complete", False
                ),
                "steps_since_progress": info.get(
                    "steps_since_progress", 0
                ),
                "stagnation_detected": info.get(
                    "stagnation_detected", False
                ),
                "truncation_reason": info.get(
                    "truncation_reason"
                ),
            })

        return result

    def _save_results(self, results):
        if not results:
            return

        with self.results_path.open(
            "w",
            newline="",
            encoding="utf-8",
        ) as file:
            writer = csv.DictWriter(
                file,
                fieldnames=list(results[0].keys()),
            )

            writer.writeheader()
            writer.writerows(results)

    def _print_summary(self, results, agent):
        if not results:
            return

        avg_reward = mean(
            row["total_reward"]
            for row in results
        )

        avg_steps = mean(
            row["steps"]
            for row in results
        )

        print()
        print("=" * 60)
        print("EXPERIMENT SUMMARY")
        print("=" * 60)

        print(f"Environment: {self.environment}")
        print(f"Mode: {self.mode}")
        print(f"Agent: {self.agent_type}")
        print(
            f"N-steps: "
            f"{self.n_steps if self.agent_type == 'dqn' else 'N/A'}"
        )
        print(f"Episodes: {len(results)}")
        print(f"Observation size: {self.input_size}")

        print(f"Average reward: {avg_reward:.4f}")
        print(f"Average steps: {avg_steps:.2f}")

        if self.environment == "simple-target":
            successes = sum(
                bool(row["success"])
                for row in results
            )

            success_rate = (
                100 * successes / len(results)
            )

            print(f"Success rate: {success_rate:.2f}%")

        else:
            avg_kills = mean(
                row["kills"]
                for row in results
            )

            avg_accuracy = mean(
                row["accuracy"]
                for row in results
            )

            completed_games = sum(
                bool(row["game_complete"])
                for row in results
            )

            stagnation_count = sum(
                bool(row["stagnation_detected"])
                for row in results
            )

            print(f"Average kills: {avg_kills:.2f}")
            print(f"Average accuracy: {avg_accuracy:.2%}")
            print(f"Games completed: {completed_games}")
            print(
                f"Stagnation episodes: "
                f"{stagnation_count}/{len(results)}"
            )

        if isinstance(agent, DQNAgent):
            print(
                f"Environment steps: "
                f"{agent.environment_steps}"
            )
            print(
                f"Gradient steps: "
                f"{agent.gradient_steps}"
            )
            print(
                f"Replay size: "
                f"{len(agent.replay_buffer)}"
            )

        print(f"Results: {self.results_path}")

        if self.mode == "train":
            print(f"Model: {self.model_path}")

        print("=" * 60)

    def run(self):
        agent = self._create_agent()
        renderer = self._create_renderer()
        debugger = self._create_debugger()

        clock = (
            pygame.time.Clock()
            if renderer is not None
            else None
        )

        results = []
        interrupted = False

        print("=" * 60)
        print("START EXPERIMENT")
        print("=" * 60)
        print(f"Environment: {self.environment}")
        print(f"Mode: {self.mode}")
        print(f"Agent: {self.agent_type}")
        print(f"N-steps: {self.n_steps}")
        print(f"Episodes: {self.episodes}")
        print(f"Max steps: {self.max_steps}")
        print(
            f"Max stagnation steps: "
            f"{self.max_stagnation_steps}"
        )
        print(f"Input size: {self.input_size}")
        print(f"Seed: {self.seed}")
        print("=" * 60)

        try:
            for episode in range(self.episodes):
                observation, info = self.env.reset(
                    seed=self.seed + episode
                )

                if isinstance(agent, DQNAgent):
                    agent.reset_episode()

                if debugger is not None:
                    debugger.reset()

                terminated = False
                truncated = False
                total_reward = 0.0
                steps = 0

                for _ in range(self.max_steps):
                    action = self._choose_action(
                        agent,
                        observation,
                    )

                    if debugger is not None:
                        debugger.record(
                            env=self.env,
                            agent=agent,
                            state=observation,
                            action=action,
                            step=steps + 1,
                        )

                    (
                        next_observation,
                        reward,
                        terminated,
                        truncated,
                        info,
                    ) = self.env.step(action)

                    self._train_agent(
                        agent=agent,
                        observation=observation,
                        action=action,
                        reward=reward,
                        next_observation=next_observation,
                        terminated=terminated,
                        truncated=truncated,
                    )

                    total_reward += float(reward)
                    steps += 1
                    observation = next_observation

                    if renderer is not None:
                        if not self._handle_render(
                            renderer, agent
                        ):
                            interrupted = True
                            truncated = True
                            break

                        clock.tick(FPS)

                    if terminated or truncated:
                        break

                result = self._make_result(
                    episode=episode,
                    steps=steps,
                    total_reward=total_reward,
                    terminated=terminated,
                    truncated=truncated,
                    info=info,
                )

                if (
                    debugger is not None
                    and info.get("truncation_reason")
                    == "stagnation"
                ):
                    path = debugger.save(
                        episode=episode + 1
                    )

                    if path is not None:
                        print(
                            f"Stagnation trajectory: {path}"
                        )

                results.append(result)

                if isinstance(agent, DQNAgent):
                    loss_text = (
                        f"{agent.last_loss:.6f}"
                        if agent.last_loss is not None
                        else "N/A"
                    )

                    print(
                        f"Episode {episode + 1}/{self.episodes} | "
                        f"Reward: {total_reward:.2f} | "
                        f"Steps: {steps} | "
                        f"Epsilon: {agent.epsilon:.4f} | "
                        f"Loss: {loss_text} | "
                        f"Buffer: {len(agent.replay_buffer)} | "
                        f"Reason: {info.get('truncation_reason')}"
                    )

                else:
                    print(
                        f"Episode {episode + 1}/{self.episodes} | "
                        f"Reward: {total_reward:.2f} | "
                        f"Steps: {steps} | "
                        f"Reason: {info.get('truncation_reason')}"
                    )

                if interrupted:
                    break

        finally:
            if renderer is not None:
                pygame.quit()

        if self.mode == "train":
            agent.save(self.model_path)

        self._save_results(results)
        self._print_summary(results, agent)

        return results
