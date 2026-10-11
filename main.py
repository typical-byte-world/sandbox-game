
import argparse

from training.runner import ExperimentRunner


def main():
    parser = argparse.ArgumentParser(
        description="Space Invaders RL Experiments"
    )

    parser.add_argument(
        "--env",
        choices=[
            "space-invaders",
            "simple-target",
        ],
        default="space-invaders",
    )

    parser.add_argument(
        "--mode",
        choices=[
            "train",
            "evaluate",
            "random",
        ],
        default="random",
    )

    parser.add_argument(
        "--episodes",
        type=int,
        default=20,
    )

    parser.add_argument(
        "--max-steps",
        type=int,
        default=3600,
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=42,
    )

    parser.add_argument(
        "--experiment",
        type=str,
        default="baseline",
    )

    parser.add_argument(
        "--render",
        action="store_true",
    )

    parser.add_argument(
        "--reward-shaping",
        action="store_true",
    )

    parser.add_argument(
        "--shaping-scale",
        type=float,
        default=1.0,
    )

    parser.add_argument(
        "--agent",
        choices=["neural", "dqn"],
        default="neural",
    )

    parser.add_argument(
        "--n-steps",
        type=int,
        default=5,
    )
    args = parser.parse_args()

    runner = ExperimentRunner(
        mode=args.mode,
        environment=args.env,
        episodes=args.episodes,
        max_steps=args.max_steps,
        seed=args.seed,
        experiment_name=args.experiment,
        render=args.render,
        reward_shaping=args.reward_shaping,
        shaping_scale=args.shaping_scale,
        agent_type=args.agent,
        n_steps=args.n_steps,
    )

    runner.run()


if __name__ == "__main__":
    main()
