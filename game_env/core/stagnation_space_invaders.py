from game_env.core.space_invaders import SpaceInvadersEnv


class StagnationSpaceInvadersEnv(SpaceInvadersEnv):
    def __init__(
        self,
        max_steps=None,
        max_stagnation_steps=300,
    ):
        if max_stagnation_steps is not None and max_stagnation_steps < 1:
            raise ValueError("max_stagnation_steps must be >= 1")

        self.max_stagnation_steps = max_stagnation_steps

        self.steps_since_progress = 0
        self.truncation_reason = None
        self.stagnation_detected = False

        super().__init__(max_steps=max_steps)

    def reset(self, seed=None):
        self.steps_since_progress = 0
        self.truncation_reason = None
        self.stagnation_detected = False

        observation, info = super().reset(seed=seed)

        return observation, self._extend_info(info)

    def step(self, action):
        previous_kills = self.stats.kills

        previous_boss_health = self.boss.health if self.boss is not None else None

        (
            observation,
            reward,
            terminated,
            truncated,
            info,
        ) = super().step(action)

        kills_increased = self.stats.kills > previous_kills

        boss_damaged = False

        if previous_boss_health is not None and self.boss is not None:
            boss_damaged = self.boss.health < previous_boss_health

        progress = kills_increased or boss_damaged

        if progress:
            self.steps_since_progress = 0
        else:
            self.steps_since_progress += 1

        stagnation_reached = (
            self.max_stagnation_steps is not None
            and self.steps_since_progress >= self.max_stagnation_steps
        )

        if terminated:
            self.truncation_reason = None

        elif truncated:
            self.truncation_reason = "time_limit"

        elif stagnation_reached:
            truncated = True

            self.stagnation_detected = True
            self.truncation_reason = "stagnation"

        info = self._extend_info(info)

        return (
            observation,
            reward,
            terminated,
            truncated,
            info,
        )

    def _extend_info(self, info):
        return {
            **info,
            "steps_since_progress": self.steps_since_progress,
            "max_stagnation_steps": self.max_stagnation_steps,
            "stagnation_detected": self.stagnation_detected,
            "truncation_reason": self.truncation_reason,
        }
