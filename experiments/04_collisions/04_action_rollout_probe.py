
"""Compare alternative first actions from identical game states."""

import argparse
import copy
import csv
import random
from pathlib import Path

import numpy as np
import torch

from agents.dqn_agent import DQNAgent
from game_env.config.display import FPS
from game_env.core.stagnation_space_invaders import (
    StagnationSpaceInvadersEnv,
)


ACTION_NAMES = ("IDLE", "LEFT", "RIGHT", "SHOOT")


def get_q_values(agent, observation):
    state = torch.as_tensor(
        observation,
        dtype=torch.float32,
        device=agent.device,
    ).unsqueeze(0)

    with torch.no_grad():
        return (
            agent.policy_network(state)
            .squeeze(0)
            .cpu()
            .numpy()
        )


def time_to_collision(player, bullet):
    """Predict rectangle collision assuming constant velocities."""

    dx = float(bullet.position.x - player.position.x)
    dy = float(bullet.position.y - player.position.y)

    vx = float(bullet.velocity.x - player.velocity.x)
    vy = float(bullet.velocity.y - player.velocity.y)

    hx = (player.rect.width + bullet.rect.width) / 2
    hy = (player.rect.height + bullet.rect.height) / 2

    entry = float("-inf")
    exit_time = float("inf")

    for distance, velocity, half_size in (
        (dx, vx, hx),
        (dy, vy, hy),
    ):
        if abs(velocity) < 1e-9:
            if abs(distance) > half_size:
                return None
            continue

        t1 = (-half_size - distance) / velocity
        t2 = (half_size - distance) / velocity

        entry = max(entry, min(t1, t2))
        exit_time = min(exit_time, max(t1, t2))

    if entry > exit_time or exit_time < 0:
        return None

    return max(0.0, entry)


def closest_threat(env):
    threats = []

    for bullet in env.enemy_bullets:
        ttc = time_to_collision(env.player, bullet)

        if ttc is not None:
            threats.append((ttc, bullet))

    if not threats:
        return None, None

    return min(threats, key=lambda item: item[0])


def rollout(
    snapshot,
    rng_state,
    agent,
    first_action,
    horizon,
    gamma,
):
    """
    Simulate one forced first action, then follow greedy DQN.

    The simulator and Python RNG are restored before each branch.
    """
    random.setstate(rng_state)

    env = copy.deepcopy(snapshot)
    observation = env.observation.get_vector(env)

    initial_lives = env.stats.lives
    initial_kills = env.stats.kills
    initial_hits = env.stats.shots_hit

    discounted_reward = 0.0
    undiscounted_reward = 0.0

    steps = 0
    terminated = False
    truncated = False
    reason = None

    for i in range(horizon):
        if i == 0:
            action = first_action
        else:
            action = agent.choose_action(observation)

        (
            observation,
            reward,
            terminated,
            truncated,
            info,
        ) = env.step(action)

        discounted_reward += (gamma**i) * reward
        undiscounted_reward += reward

        steps += 1

        if terminated or truncated:
            reason = info.get("truncation_reason")
            break

    return {
        "steps_simulated": steps,
        "lives_lost": initial_lives - env.stats.lives,
        "kills_gained": env.stats.kills - initial_kills,
        "hits_gained": env.stats.shots_hit - initial_hits,
        "discounted_reward": discounted_reward,
        "total_reward": undiscounted_reward,
        "terminated": terminated,
        "truncated": truncated,
        "game_complete": env.stats.game_complete,
        "truncation_reason": reason or "",
        "final_player_x": float(env.player.position.x),
    }


def evaluate_state(
    env,
    agent,
    episode,
    step,
    horizon,
    gamma,
    ttc,
):
    observation = env.observation.get_vector(env)
    q_values = get_q_values(agent, observation)

    chosen_index = int(np.argmax(q_values))

    snapshot = copy.deepcopy(env)
    rng_state = random.getstate()

    outcomes = []

    try:
        for action_index, action in enumerate(agent.actions):
            result = rollout(
                snapshot=snapshot,
                rng_state=rng_state,
                agent=agent,
                first_action=action,
                horizon=horizon,
                gamma=gamma,
            )

            outcomes.append({
                "action_index": action_index,
                "action": ACTION_NAMES[action_index],
                **result,
            })

    finally:
        # Do not change the original episode's random sequence.
        random.setstate(rng_state)

    chosen_result = outcomes[chosen_index]

    # Primary comparison: preserve more lives.
    # Secondary: obtain higher discounted reward.
    best_result = min(
        outcomes,
        key=lambda r: (
            r["lives_lost"],
            -r["discounted_reward"],
        ),
    )

    avoidable_damage = (
        chosen_result["lives_lost"]
        > min(r["lives_lost"] for r in outcomes)
    )

    rows = []

    for outcome in outcomes:
        rows.append({
            "episode": episode,
            "step": step,
            "ttc_seconds": ttc,
            "bullet_count": len(env.enemy_bullets),
            "player_x": float(env.player.position.x),
            "player_y": float(env.player.position.y),
            "player_vx": float(env.player.velocity.x),
            "player_vy": float(env.player.velocity.y),
            "initial_lives": env.stats.lives,
            "chosen_action": ACTION_NAMES[chosen_index],
            "best_tested_action": best_result["action"],
            "avoidable_damage": avoidable_damage,
            "q_idle": float(q_values[0]),
            "q_left": float(q_values[1]),
            "q_right": float(q_values[2]),
            "q_shoot": float(q_values[3]),
            "q_action": float(q_values[outcome["action_index"]]),
            **outcome,
        })

    return rows


def run(args):
    if args.horizon < 1:
        raise ValueError("--horizon must be >= 1")

    if args.sample_gap < 1:
        raise ValueError("--sample-gap must be >= 1")

    if args.samples < 1:
        raise ValueError("--samples must be >= 1")

    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)

    env = StagnationSpaceInvadersEnv(
        max_steps=args.max_steps,
        max_stagnation_steps=300,
    )

    observation, _ = env.reset(seed=args.seed)

    agent = DQNAgent(
        input_size=len(observation),
        training=False,
        n_steps=args.n_steps,
        seed=args.seed,
    )

    if len(agent.actions) != 4:
        raise ValueError(
            "This experiment expects the original 4-action space."
        )

    model_path = (
        Path("models")
        / "space-invaders"
        / "dqn"
        / f"{args.experiment}.pt"
    )

    if not model_path.exists():
        raise FileNotFoundError(model_path)

    agent.load(model_path)
    agent.policy_network.eval()

    output = (
        Path("results")
        / "space-invaders"
        / "dqn"
        / args.experiment
        / "action_rollout_probe.csv"
    )

    output.parent.mkdir(parents=True, exist_ok=True)

    all_rows = []
    analyzed = 0

    for episode in range(1, args.episodes + 1):
        observation, _ = env.reset(
            seed=args.seed + episode - 1
        )

        last_sample = -10**9

        for step in range(1, args.max_steps + 1):
            ttc, bullet = closest_threat(env)

            interesting = (
                bullet is not None
                and ttc is not None
                and ttc <= args.ttc_threshold
            )

            spaced = step - last_sample >= args.sample_gap

            # Leave enough room for the full rollout.
            enough_time = (
                env.max_steps is None
                or env.steps + args.horizon <= env.max_steps
            )

            if interesting and spaced and enough_time:
                rows = evaluate_state(
                    env=env,
                    agent=agent,
                    episode=episode,
                    step=step,
                    horizon=args.horizon,
                    gamma=args.gamma,
                    ttc=ttc,
                )

                all_rows.extend(rows)
                analyzed += 1
                last_sample = step

                if analyzed >= args.samples:
                    break

            # Continue the original, unmodified episode.
            action = agent.choose_action(observation)

            (
                observation,
                _,
                terminated,
                truncated,
                _,
            ) = env.step(action)

            if terminated or truncated:
                break

        print(
            f"Episode {episode}/{args.episodes} | "
            f"Samples: {analyzed}/{args.samples}"
        )

        if analyzed >= args.samples:
            break

    if not all_rows:
        print("No threatening states were found.")
        return

    with output.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=list(all_rows[0].keys()),
        )
        writer.writeheader()
        writer.writerows(all_rows)

    chosen_rows = [
        row
        for row in all_rows
        if row["action"] == row["chosen_action"]
    ]

    damaged = [
        row
        for row in chosen_rows
        if row["lives_lost"] > 0
    ]

    avoidable = [
        row
        for row in chosen_rows
        if row["avoidable_damage"]
    ]

    print("\nACTION ROLLOUT PROBE")
    print("=" * 55)
    print(f"Model: {model_path}")
    print(f"States analyzed: {analyzed}")
    print(f"Horizon: {args.horizon} steps")
    print(f"Damage after chosen action: {len(damaged)}")
    print(f"Avoidable damage: {len(avoidable)}")
    print(f"Output: {output}")

    for name in ACTION_NAMES:
        subset = [
            row
            for row in all_rows
            if row["action"] == name
        ]

        mean_lives_lost = np.mean([
            row["lives_lost"]
            for row in subset
        ])

        mean_reward = np.mean([
            row["discounted_reward"]
            for row in subset
        ])

        print(
            f"{name:>6} | "
            f"Mean lives lost: {mean_lives_lost:.3f} | "
            f"Mean discounted reward: {mean_reward:.3f}"
        )


def parse_args():
    parser = argparse.ArgumentParser(
        description="Counterfactual action rollouts for DQN"
    )

    parser.add_argument(
        "--experiment",
        default="dqn_dodge_v1",
    )
    parser.add_argument("--episodes", type=int, default=30)
    parser.add_argument("--samples", type=int, default=100)
    parser.add_argument("--seed", type=int, default=10000)
    parser.add_argument("--max-steps", type=int, default=3600)
    parser.add_argument("--n-steps", type=int, default=5)
    parser.add_argument("--horizon", type=int, default=15)
    parser.add_argument("--gamma", type=float, default=0.99)
    parser.add_argument(
        "--ttc-threshold",
        type=float,
        default=0.5,
    )
    parser.add_argument("--sample-gap", type=int, default=15)

    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
