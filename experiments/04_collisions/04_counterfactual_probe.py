
"""Counterfactual sensitivity probe for a trained Space Invaders DQN."""

import argparse
import csv
from pathlib import Path

import numpy as np
import torch

from agents.dqn_agent import DQNAgent
from game_env.config.display import FPS, WIDTH
from game_env.core.stagnation_space_invaders import StagnationSpaceInvadersEnv


ACTION_NAMES = ["IDLE", "LEFT", "RIGHT", "SHOOT"]


def q_values(agent, observation):
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


def predicted_impact_time(player, bullet):
    """Constant-velocity prediction of rectangle overlap."""
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


def find_threat(env):
    candidates = []

    for bullet in env.enemy_bullets:
        ttc = predicted_impact_time(env.player, bullet)

        if ttc is not None:
            candidates.append((ttc, bullet))

    if not candidates:
        return None, None

    return min(candidates, key=lambda item: item[0])


def bullet_slice(observation_encoder):
    """Locate enemy bullet slots from the observation contract."""
    cfg = observation_encoder.config

    start = (
        observation_encoder.PLAYER_FEATURES
        + cfg.max_enemies * observation_encoder.ENEMY_FEATURES
        + cfg.max_player_bullets
        * observation_encoder.BULLET_FEATURES
    )

    width = (
        cfg.max_enemy_bullets
        * observation_encoder.BULLET_FEATURES
    )

    return slice(start, start + width)


def make_counterfactuals(env, original, threat):
    """
    Create alternative observations without modifying the environment.

    Bullet feature order:
    [mask, x, y, relative_x, relative_y,
     width, height, velocity_x, velocity_y]
    """
    encoder = env.observation
    cfg = encoder.config

    bullet_region = bullet_slice(encoder)
    stride = encoder.BULLET_FEATURES

    variants = {
        "original": original.copy(),
    }

    # Counterfactual 1: remove all enemy bullets.
    no_bullets = original.copy()
    no_bullets[bullet_region] = 0.0

    # Global features:
    # [wave, enemy_count, enemy_bullet_count, steps]
    global_start = len(original) - encoder.GLOBAL_FEATURES
    no_bullets[global_start + 2] = 0.0

    variants["no_bullets"] = no_bullets

    if threat is None:
        return variants

    ordered_bullets = sorted(
        env.enemy_bullets,
        key=lambda obj: (
            obj.position.x,
            obj.position.y,
        ),
    )

    try:
        threat_index = next(
            i
            for i, bullet in enumerate(ordered_bullets)
            if bullet is threat
        )
    except StopIteration:
        return variants

    # Only manipulate bullets represented in observation.
    if threat_index >= cfg.max_enemy_bullets:
        return variants

    for name, offset_px in (
        ("bullet_left", -120.0),
        ("bullet_right", 120.0),
    ):
        modified = original.copy()

        relative_region = modified[bullet_region].copy()

        slots = relative_region.reshape(
            cfg.max_enemy_bullets,
            stride,
        )

        # Keep the bullet inside the screen.
        old_x = float(threat.position.x)
        new_x = float(np.clip(
            old_x + offset_px,
            0.0,
            WIDTH,
        ))

        actual_offset = new_x - old_x
        normalized_offset = actual_offset / WIDTH

        # Absolute and relative X must change together.
        slots[threat_index, 1] += normalized_offset
        slots[threat_index, 3] += normalized_offset

        # Restore canonical ordering by X, then Y.
        active_count = len(ordered_bullets)

        active_slots = slots[:active_count].copy()

        order = sorted(
            range(active_count),
            key=lambda i: (
                active_slots[i, 1],
                active_slots[i, 2],
            ),
        )

        slots[:active_count] = active_slots[order]

        modified[bullet_region] = slots.reshape(-1)

        variants[name] = modified

    return variants


def analyze_state(env, agent, episode, step):
    observation = env.observation.get_vector(env)

    ttc, threat = find_threat(env)

    variants = make_counterfactuals(
        env,
        observation,
        threat,
    )

    original_q = q_values(
        agent,
        variants["original"],
    )

    rows = []

    for name, state in variants.items():
        q = q_values(agent, state)

        delta = q - original_q
        selected = int(np.argmax(q))

        rows.append({
            "episode": episode,
            "step": step,
            "variant": name,
            "ttc_seconds": (
                "" if ttc is None else float(ttc)
            ),
            "bullet_count": len(env.enemy_bullets),
            "player_x": float(env.player.position.x),
            "player_vx": float(env.player.velocity.x),
            "threat_x": (
                "" if threat is None
                else float(threat.position.x)
            ),
            "threat_y": (
                "" if threat is None
                else float(threat.position.y)
            ),
            "q_idle": float(q[0]),
            "q_left": float(q[1]),
            "q_right": float(q[2]),
            "q_shoot": float(q[3]),
            "best_action": ACTION_NAMES[selected],
            "max_abs_q_delta": float(
                np.max(np.abs(delta))
            ),
            "l2_q_delta": float(
                np.linalg.norm(delta)
            ),
            "action_changed": (
                selected != int(np.argmax(original_q))
            ),
        })

    return rows


def run(args):
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

    output_path = (
        Path("results")
        / "space-invaders"
        / "dqn"
        / args.experiment
        / "counterfactual_probe.csv"
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    rows = []
    samples = 0

    for episode in range(1, args.episodes + 1):
        observation, _ = env.reset(
            seed=args.seed + episode - 1
        )

        previous_sample_step = -10**9

        for step in range(1, args.max_steps + 1):
            ttc, threat = find_threat(env)

            # Probe only states with an approaching threat.
            interesting = (
                threat is not None
                and ttc is not None
                and ttc <= args.ttc_threshold
            )

            enough_spacing = (
                step - previous_sample_step
                >= args.sample_gap
            )

            if interesting and enough_spacing:
                rows.extend(
                    analyze_state(
                        env,
                        agent,
                        episode,
                        step,
                    )
                )

                samples += 1
                previous_sample_step = step

                if samples >= args.samples:
                    break

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
            f"Samples: {samples}/{args.samples}"
        )

        if samples >= args.samples:
            break

    if not rows:
        print("No threatening states found.")
        print("Try increasing --episodes or --ttc-threshold.")
        return

    with output_path.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=list(rows[0].keys()),
        )

        writer.writeheader()
        writer.writerows(rows)

    original_rows = [
        row for row in rows
        if row["variant"] == "original"
    ]

    print("\nCOUNTERFACTUAL PROBE")
    print("=" * 55)
    print(f"Model: {model_path}")
    print(f"States analyzed: {len(original_rows)}")
    print(f"Output: {output_path}")

    for variant in (
        "no_bullets",
        "bullet_left",
        "bullet_right",
    ):
        selected_rows = [
            row for row in rows
            if row["variant"] == variant
        ]

        if not selected_rows:
            continue

        changes = sum(
            bool(row["action_changed"])
            for row in selected_rows
        )

        avg_delta = np.mean([
            row["max_abs_q_delta"]
            for row in selected_rows
        ])

        print(
            f"{variant:>14} | "
            f"Changed: {changes}/{len(selected_rows)} | "
            f"Mean max |ΔQ|: {avg_delta:.4f}"
        )


def parse_args():
    parser = argparse.ArgumentParser(
        description="Counterfactual DQN state probe"
    )

    parser.add_argument(
        "--experiment",
        default="dqn_dodge_v1",
    )

    parser.add_argument(
        "--episodes",
        type=int,
        default=30,
    )

    parser.add_argument(
        "--samples",
        type=int,
        default=100,
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=10000,
    )

    parser.add_argument(
        "--max-steps",
        type=int,
        default=3600,
    )

    parser.add_argument(
        "--n-steps",
        type=int,
        default=5,
    )

    parser.add_argument(
        "--ttc-threshold",
        type=float,
        default=0.5,
    )

    parser.add_argument(
        "--sample-gap",
        type=int,
        default=15,
    )

    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
