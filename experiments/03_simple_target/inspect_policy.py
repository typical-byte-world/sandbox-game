
import numpy as np
import torch

from game_env.agent.NeuralAgent import NeuralAgent


agent = NeuralAgent(
    input_size=2,
    training=False,
)

agent.load(
    "models/simple-target/target_01.pt"
)

agent.network.eval()

states = [
    (0.2, 0.8),
    (0.8, 0.2),
    (0.5, 0.5),
    (0.50, 0.53),
    (0.53, 0.50),
    (0.1, 0.9),
    (0.9, 0.1),
]

print("Actions:", agent.actions)

for state in states:
    observation = np.array(
        state,
        dtype=np.float32,
    )

    with torch.no_grad():
        q_values = agent.network(
            agent._to_tensor(observation)
        )

    best_index = torch.argmax(q_values).item()

    print(
        f"State: {state} | "
        f"Q: {q_values.tolist()} | "
        f"Action: {agent.actions[best_index]}"
    )
