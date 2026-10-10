import numpy as np

from game_env.agent.NeuralAgent import NeuralAgent

agent = NeuralAgent(training=False)
agent.load("models/space_invaders.npz")

base_state = np.array([
    0.5, 0.94,
    0, 0, 0,
    1, 0, -0.3,
    0, 0, 0,
], dtype=np.float64)

for enemy_dx in [-0.5, 0.0, 0.5]:
    state = base_state.copy()
    state[6] = enemy_dx

    q_values = agent.network.forward(state)

    hidden = agent.network.last_a1
    active = np.count_nonzero(hidden)

    print(f"\nenemy_dx: {enemy_dx:+.1f}")

    print("Weights1:")
    print(agent.network.weights1)

    print("Bias1:")
    print(agent.network.bias1)

    print("Bias2:")
    print(agent.network.bias2)
    # print(f"Q-values: {np.round(q_values, 4)}")
    # print(f"Hidden: {np.round(hidden, 4)}")
    # print(f"Active neurons: {active}/16")