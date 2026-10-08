import numpy as np

from game_env.controllers.action import Action

import numpy as np


class NeuralNet:
    def __init__(
        self,
        input_size=11,
        hidden_size=16,
        output_size=18,
    ):
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size

        self.weights1 = (
            np.random.randn(hidden_size, input_size)
            * np.sqrt(1 / input_size)
        )
        self.bias1 = np.zeros(hidden_size)

        self.weights2 = (
            np.random.randn(output_size, hidden_size)
            * np.sqrt(1 / hidden_size)
        )
        self.bias2 = np.zeros(output_size)

    def forward(self, x):
        z1 = np.dot(self.weights1, x) + self.bias1
        a1 = np.maximum(0, z1)

        z2 = np.dot(self.weights2, a1) + self.bias2

        return z2

    def train(self, x, action_index, target, learning_rate):
        z1 = np.dot(self.weights1, x) + self.bias1
        a1 = np.maximum(0, z1)

        q_values = np.dot(self.weights2, a1) + self.bias2

        prediction = q_values[action_index]

        loss = 0.5 * (prediction - target) ** 2

        gradient_output = np.zeros(self.output_size)
        gradient_output[action_index] = prediction - target

        gradient_weights2 = np.outer(
            gradient_output,
            a1,
        )

        gradient_bias2 = gradient_output

        gradient_a1 = np.dot(
            self.weights2.T,
            gradient_output,
        )

        gradient_z1 = gradient_a1 * (z1 > 0)

        gradient_weights1 = np.outer(
            gradient_z1,
            x,
        )

        gradient_bias1 = gradient_z1

        self.weights2 -= learning_rate * gradient_weights2
        self.bias2 -= learning_rate * gradient_bias2

        self.weights1 -= learning_rate * gradient_weights1
        self.bias1 -= learning_rate * gradient_bias1

        return loss




if __name__ == '__main__':
    x = np.array([
        0.9875,
        0.99,
        1.0,
        0.0,
        -0.0991,
        1.0,
        -0.5416,
        -0.3582,
        0.0,
        0.0,
        0.0,
    ], dtype=np.float32)

    network = NeuralNet()

    y = network.forward(x)

    # print(y)
    actions = Action.all_actions()

    for action, q_value in zip(actions, y):
        print(action, q_value)