class GameStats:
    def __init__(self):
        self.reset()

    def reset(self):
        self.score = 0
        self.kills = 0
        self.shots_fired = 0
        self.shots_hit = 0
        self.survival_time = 0.0
        self.wave = 1
        self.lives = 3

    @property
    def accuracy(self):
        if self.shots_fired == 0:
            return 0.0

        return self.shots_hit / self.shots_fired * 100