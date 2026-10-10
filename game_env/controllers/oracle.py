
from game_env.controllers.action import Action


class OracleController:
    def __init__(
        self,
        width=100,
        hit_radius=5,
    ):
        self.width = width
        self.hit_radius = hit_radius

    def choose_action(self, observation):
        player_x = float(observation[0]) * self.width
        target_x = float(observation[1]) * self.width

        distance = target_x - player_x

        if abs(distance) <= self.hit_radius + 1e-4:
            return Action(shoot=True)

        if distance > 0:
            return Action(move_x=1)

        return Action(move_x=-1)
