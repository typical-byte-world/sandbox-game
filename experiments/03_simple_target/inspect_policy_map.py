
import numpy as np
import torch
import matplotlib.pyplot as plt

from game_env.agent.NeuralAgent import NeuralAgent


agent = NeuralAgent(input_size=2, training=False)
agent.load("models/simple-target/target_01.pt")
agent.network.eval()

positions = np.linspace(0, 1, 101)

player_x, target_x = np.meshgrid(
    positions, positions
)

states = np.stack(
    [player_x.ravel(), target_x.ravel()],
    axis=1
).astype(np.float32)

with torch.no_grad():
    q_values = agent.network(
        torch.from_numpy(states)
    )
    actions = q_values.argmax(dim=1).numpy()

policy_map = actions.reshape(player_x.shape)

plt.figure(figsize=(8, 7))

plt.imshow(
    policy_map,
    origin="lower",
    extent=[0, 1, 0, 1],
    interpolation="nearest",
    aspect="equal",
    vmin=0,
    vmax=3,
    cmap="viridis",
)

plt.colorbar(
    ticks=[0, 1, 2, 3],
    label="Action: 0=IDLE, 1=LEFT, 2=RIGHT, 3=SHOOT"
)

plt.xlabel("Player X")
plt.ylabel("Target X")
plt.title("Learned Policy — SimpleTargetEnv")

plt.tight_layout()
plt.show()
