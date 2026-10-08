from collections import deque


class TrainingHistory:
    def __init__(self, max_length=300):
        self.rewards = deque(maxlen=max_length)
        self.losses = deque(maxlen=max_length)
        self.max_q_values = deque(maxlen=max_length)

    def add(self, reward, loss, max_q):
        self.rewards.append(reward)
        self.losses.append(loss)
        self.max_q_values.append(max_q)