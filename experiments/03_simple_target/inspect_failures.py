
from collections import Counter

from game_env.agent.NeuralAgent import NeuralAgent
from game_env.core.simple_target import SimpleTargetEnv


agent = NeuralAgent(input_size=2, training=False)
agent.load("models/simple-target/target_01.pt")
agent.network.eval()

env = SimpleTargetEnv(max_steps=100)

action_names = ["IDLE", "LEFT", "RIGHT", "SHOOT"]

failures = 0

for episode in range(1, 101):
    observation, info = env.reset(seed=42 + episode)

    trajectory = []

    while True:
        action = agent.choose_action(observation)
        action_index = agent.actions.index(action)

        trajectory.append({
            "step": info["steps"],
            "player_x": info["player_x"],
            "target_x": info["target_x"],
            "distance": info["distance"],
            "action": action_names[action_index],
        })

        observation, reward, terminated, truncated, info = (
            env.step(action)
        )

        if terminated or truncated:
            break

    if not info["success"]:
        failures += 1

        print(f"\nFAILED EPISODE {episode}")
        print(
            f"Start: {trajectory[0]['player_x']} -> "
            f"Target: {trajectory[0]['target_x']}"
        )

        print(
            "Actions:",
            dict(Counter(
                step["action"]
                for step in trajectory
            ))
        )

        print("Last 10 steps:")

        for step in trajectory[-10:]:
            print(step)

        if failures >= 3:
            break
