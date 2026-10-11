import pandas as pd
import matplotlib.pyplot as plt

path = "results/simple-target/dqn/dqn_n5_train.csv"

df = pd.read_csv(path)

window = 100

df["success_rate"] = (
    df["success"].astype(int)
    .rolling(window, min_periods=1)
    .mean() * 100
)

df["avg_reward"] = (
    df["total_reward"]
    .rolling(window, min_periods=1)
    .mean()
)

df["avg_steps"] = (
    df["steps"]
    .rolling(window, min_periods=1)
    .mean()
)

fig, axes = plt.subplots(3, 1, figsize=(12, 10))

axes[0].plot(df["episode"], df["success_rate"])
axes[0].set_title("Success Rate (rolling 100)")
axes[0].set_ylabel("Success %")
axes[0].set_ylim(0, 100)

axes[1].plot(df["episode"], df["avg_reward"])
axes[1].set_title("Average Reward (rolling 100)")
axes[1].set_ylabel("Reward")

axes[2].plot(df["episode"], df["avg_steps"])
axes[2].set_title("Average Steps (rolling 100)")
axes[2].set_ylabel("Steps")
axes[2].set_xlabel("Episode")

plt.tight_layout()
plt.show()