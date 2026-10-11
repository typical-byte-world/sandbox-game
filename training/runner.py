"""Coordinate episode execution, learning, rendering, and reporting."""

import random

import numpy as np
import pygame
import torch

from agents.dqn_agent import DQNAgent
from game_env.config.display import FPS
from training.config import ExperimentConfig
from training.factories import (
    create_agent,
    create_debugger,
    create_environment,
    create_renderer,
)
from training.paths import ExperimentPaths
from training.reporting import make_result, print_summary, save_results


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
        self.config = ExperimentConfig(
            mode=mode,
            environment=environment,
            episodes=episodes,
            max_steps=max_steps,
            seed=seed,
            experiment_name=experiment_name,
            render=render,
            reward_shaping=reward_shaping,
            shaping_scale=shaping_scale,
            agent_type=agent_type,
            n_steps=n_steps,
            max_stagnation_steps=max_stagnation_steps,
            debug_last_steps=debug_last_steps,
        )
        self.mode = self.config.mode
        self.environment = self.config.environment
        self.episodes = self.config.episodes
        self.max_steps = self.config.max_steps
        self.seed = self.config.seed
        self.experiment_name = self.config.experiment_name
        self.render = self.config.render
        self.reward_shaping = self.config.reward_shaping
        self.shaping_scale = self.config.shaping_scale
        self.agent_type = self.config.agent_type
        self.n_steps = self.config.n_steps
        self.max_stagnation_steps = self.config.max_stagnation_steps
        self.debug_last_steps = self.config.debug_last_steps

        random.seed(seed)
        np.random.seed(seed)
        torch.manual_seed(seed)

        self.env = self._create_environment()

        observation, _ = self.env.reset(seed=seed)
        self.input_size = len(observation)

        paths = ExperimentPaths.for_experiment(
            environment, agent_type, experiment_name, mode
        )
        self.model_path = paths.model
        self.results_path = paths.results
        paths.create_directories()

    def _create_environment(self):
        return create_environment(
            environment=self.environment,
            max_stagnation_steps=self.max_stagnation_steps,
            max_steps=self.max_steps,
            reward_shaping=self.reward_shaping,
            shaping_scale=self.shaping_scale,
        )

    def _create_agent(self):
        return create_agent(
            agent_type=self.agent_type,
            input_size=self.input_size,
            mode=self.mode,
            model_path=self.model_path,
            n_steps=self.n_steps,
            seed=self.seed,
        )

    def _create_renderer(self):
        return create_renderer(
            environment=self.environment,
            render=self.render,
        )

    def _create_debugger(self):
        return create_debugger(
            agent_type=self.agent_type,
            debug_last_steps=self.debug_last_steps,
            environment=self.environment,
            experiment_name=self.experiment_name,
            mode=self.mode,
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

    def _make_result(self, episode, steps, total_reward, terminated, truncated, info):
        return make_result(
            episode=episode,
            steps=steps,
            total_reward=total_reward,
            terminated=terminated,
            truncated=truncated,
            info=info,
            environment=self.environment,
            seed=self.seed,
        )

    def _save_results(self, results):
        return save_results(
            results=results,
            results_path=self.results_path,
        )

    def _print_summary(self, results, agent):
        return print_summary(
            results=results,
            agent=agent,
            agent_type=self.agent_type,
            environment=self.environment,
            input_size=self.input_size,
            mode=self.mode,
            model_path=self.model_path,
            n_steps=self.n_steps,
            results_path=self.results_path,
        )

    def _run_episode(self, episode, agent, renderer, debugger, clock):
        interrupted = False
        observation, info = self.env.reset(seed=self.seed + episode)

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
                if not self._handle_render(renderer, agent):
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
        return result, info, interrupted, steps, total_reward

    def run(self):
        agent = self._create_agent()
        renderer = self._create_renderer()
        debugger = self._create_debugger()

        clock = pygame.time.Clock() if renderer is not None else None

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
        print(f"Max stagnation steps: {self.max_stagnation_steps}")
        print(f"Input size: {self.input_size}")
        print(f"Seed: {self.seed}")
        print("=" * 60)

        try:
            for episode in range(self.episodes):
                result, info, interrupted, steps, total_reward = self._run_episode(
                    episode, agent, renderer, debugger, clock
                )

                if (
                    debugger is not None
                    and info.get("truncation_reason") == "stagnation"
                ):
                    path = debugger.save(episode=episode + 1)

                    if path is not None:
                        print(f"Stagnation trajectory: {path}")

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
