"""Episode metrics, CSV persistence, and console summaries."""

import csv
from statistics import mean

from agents.dqn_agent import DQNAgent


def make_result(
    episode, steps, total_reward, terminated, truncated, info, environment, seed
):
    result = {
        "episode": episode,
        "seed": seed + episode,
        "steps": steps,
        "total_reward": total_reward,
        "terminated": terminated,
        "truncated": truncated,
    }
    if environment == "simple-target":
        result.update(
            {
                "success": bool(info.get("success", False)),
                "final_distance": info.get("distance", info.get("final_distance")),
            }
        )
    else:
        shots_fired = info.get("shots_fired", 0)
        shots_hit = info.get("shots_hit", 0)
        accuracy = shots_hit / shots_fired if shots_fired > 0 else 0.0
        result.update(
            {
                "wave": info.get("wave", 0),
                "survival_time": info.get("survival_time", 0.0),
                "shots_fired": shots_fired,
                "shots_hit": shots_hit,
                "accuracy": accuracy,
                "kills": info.get("kills", 0),
                "score": info.get("score", 0),
                "lives_remaining": info.get("lives", 0),
                "game_complete": info.get("game_complete", False),
                "steps_since_progress": info.get("steps_since_progress", 0),
                "stagnation_detected": info.get("stagnation_detected", False),
                "truncation_reason": info.get("truncation_reason"),
            }
        )
    return result


def save_results(results, results_path):
    if not results:
        return
    with results_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(results[0].keys()))
        writer.writeheader()
        writer.writerows(results)


def print_summary(
    results,
    agent,
    agent_type,
    environment,
    input_size,
    mode,
    model_path,
    n_steps,
    results_path,
):
    if not results:
        return
    avg_reward = mean((row["total_reward"] for row in results))
    avg_steps = mean((row["steps"] for row in results))
    print()
    print("=" * 60)
    print("EXPERIMENT SUMMARY")
    print("=" * 60)
    print(f"Environment: {environment}")
    print(f"Mode: {mode}")
    print(f"Agent: {agent_type}")
    print(f"N-steps: {(n_steps if agent_type == 'dqn' else 'N/A')}")
    print(f"Episodes: {len(results)}")
    print(f"Observation size: {input_size}")
    print(f"Average reward: {avg_reward:.4f}")
    print(f"Average steps: {avg_steps:.2f}")
    if environment == "simple-target":
        successes = sum((bool(row["success"]) for row in results))
        success_rate = 100 * successes / len(results)
        print(f"Success rate: {success_rate:.2f}%")
    else:
        avg_kills = mean((row["kills"] for row in results))
        avg_accuracy = mean((row["accuracy"] for row in results))
        completed_games = sum((bool(row["game_complete"]) for row in results))
        stagnation_count = sum((bool(row["stagnation_detected"]) for row in results))
        print(f"Average kills: {avg_kills:.2f}")
        print(f"Average accuracy: {avg_accuracy:.2%}")
        print(f"Games completed: {completed_games}")
        print(f"Stagnation episodes: {stagnation_count}/{len(results)}")
    if isinstance(agent, DQNAgent):
        print(f"Environment steps: {agent.environment_steps}")
        print(f"Gradient steps: {agent.gradient_steps}")
        print(f"Replay size: {len(agent.replay_buffer)}")
    print(f"Results: {results_path}")
    if mode == "train":
        print(f"Model: {model_path}")
    print("=" * 60)
