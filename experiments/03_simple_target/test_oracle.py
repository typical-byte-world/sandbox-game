
from statistics import mean

from game_env.core.simple_target import SimpleTargetEnv
from game_env.controllers.oracle import OracleController


EPISODES = 1000
MAX_STEPS = 100

env = SimpleTargetEnv(
    max_steps=MAX_STEPS,
    reward_shaping=False,
)

agent = OracleController(
    width=env.width,
    hit_radius=env.hit_radius,
)

results = []
failures = []

for episode in range(1, EPISODES + 1):
    observation, info = env.reset(
        seed=10000 + episode
    )

    initial_player_x = info["player_x"]
    initial_target_x = info["target_x"]

    while True:
        action = agent.choose_action(observation)

        (
            observation,
            reward,
            terminated,
            truncated,
            info,
        ) = env.step(action)

        if terminated or truncated:
            break

    results.append({
        "success": info["success"],
        "steps": info["steps"],
        "distance": info["distance"],
    })

    if not info["success"]:
        failures.append({
            "episode": episode,
            "player_x": initial_player_x,
            "target_x": initial_target_x,
            "final_distance": info["distance"],
        })

success_rate = mean(
    result["success"]
    for result in results
)

average_steps = mean(
    result["steps"]
    for result in results
)

print("\nORACLE EVALUATION")
print("=" * 40)

print(f"Episodes: {EPISODES}")
print(f"Success rate: {success_rate:.2%}")
print(f"Average steps: {average_steps:.2f}")
print(f"Failures: {len(failures)}")

if failures:
    print("\nFirst failures:")

    for failure in failures[:10]:
        print(failure)
