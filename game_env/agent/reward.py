from game_env.settings import ENEMY_HIT, LOST_LIFE, BOSS_DESTROY, DIE, NOTHIG_HAPPEN, SURVIVAL, AIM_REWARD

class Reward:
    def __init__(self):
        self.enemy_hit = ENEMY_HIT
        self.lost_life = LOST_LIFE
        self.boss_destroy = BOSS_DESTROY
        self.die = DIE
        self.nothing_happen = NOTHIG_HAPPEN
        self.survival = SURVIVAL
        self.aim_reward = AIM_REWARD

    def calculate(self, previous_stats, current_stats, previous_x_player, previous_x_enemy, current_x_player, current_x_enemy):
        reward = 0

        reward += (current_stats.shots_hit - previous_stats.shots_hit) * self.enemy_hit

        reward += (previous_stats.lives - current_stats.lives) * self.lost_life

        if current_stats.game_complete:
            reward += self.boss_destroy

        if current_stats.lives <= 0:
            reward += self.die

        # reward += self.survival

        previous_x_distance = abs(previous_x_player - previous_x_enemy)
        current_x_distance = abs(current_x_player - current_x_enemy)

        if current_x_distance < previous_x_distance:
            reward += self.aim_reward

        elif current_x_distance > previous_x_distance:
            reward -= self.aim_reward

        return reward

