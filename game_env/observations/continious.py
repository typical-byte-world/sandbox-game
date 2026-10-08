import numpy as np

from game_env.settings import WIDTH, HEIGHT




class Observation:
    def __init__(self):
        self.width = WIDTH
        self.height = HEIGHT

    def get_observation(self, game):

        player_x = game.player.position.x
        player_y = game.player.position.y

        # enemy
        if game.enemies:
            enemy_present = 1
            closest_enemy = min(
                game.enemies,
                key=lambda enemy: enemy.position.distance_to(game.player.position)
            )
            enemy_dx = (closest_enemy.position.x - player_x) / self.width
            enemy_dy = (closest_enemy.position.y - player_y) / self.height
        else:
            enemy_present = 0
            enemy_dx = 0
            enemy_dy = 0


        # enemy bullet
        if game.enemy_bullets:
            enemy_bullet_present = 1
            closest_enemy_bullet = min(
                game.enemy_bullets,
                key=lambda enemy_bullet: enemy_bullet.position.distance_to(game.player.position)
            )
            enemy_bullet_dx = (closest_enemy_bullet.position.x - player_x) / self.width
            enemy_bullet_dy = (closest_enemy_bullet.position.y - player_y) / self.height
        else:
            enemy_bullet_present = 0
            enemy_bullet_dx = 0
            enemy_bullet_dy = 0


        # player bullet
        if game.bullets:
            player_bullet_present = 1
            closest_player_bullet = min(
                game.bullets,
                key=lambda player_bullet: player_bullet.position.distance_to(game.player.position)
            )
            player_bullet_dx = (closest_player_bullet.position.x - player_x) / self.width
            player_bullet_dy = (closest_player_bullet.position.y - player_y) / self.height
        else:
            player_bullet_present = 0
            player_bullet_dx = 0
            player_bullet_dy = 0

        player_x /= self.width
        player_y /= self.height


        return {
            'player_x': player_x,
            'player_y': player_y,

            'player_bullet_present': player_bullet_present,
            'player_bullet_dx': player_bullet_dx,
            'player_bullet_dy': player_bullet_dy,

            'enemy_present': enemy_present,
            'enemy_dx': enemy_dx,
            'enemy_dy': enemy_dy,

            'enemy_bullet_present': enemy_bullet_present,
            'enemy_bullet_dx': enemy_bullet_dx,
            'enemy_bullet_dy': enemy_bullet_dy
        }


    def get_vector(self, game):
        observation = self.get_observation(game)

        return np.array([
            observation["player_x"],
            observation["player_y"],

            observation["player_bullet_present"],
            observation["player_bullet_dx"],
            observation["player_bullet_dy"],

            observation["enemy_present"],
            observation["enemy_dx"],
            observation["enemy_dy"],

            observation["enemy_bullet_present"],
            observation["enemy_bullet_dx"],
            observation["enemy_bullet_dy"],
        ], dtype=np.float32)