
from game_env.settings import ZONES, WIDTH, HEIGHT


class Observation:
    def __init__(self):

        self.zones = ZONES

    def get_observation(self, game):
        player_x = game.player.position.x
        player_y = game.player.position.y

        if game.bullets:
            closest_bullet = min(
                game.bullets,
                key=lambda bullet: bullet.position.distance_to(game.player.position)
            )
            bullet_x = closest_bullet.position.x
            bullet_y = closest_bullet.position.y

        else:
            bullet_x = -1
            bullet_y = -1


        if game.enemy_bullets:
            closest_enemy_bullet = min(
                game.enemy_bullets,
                key=lambda bullet: bullet.position.distance_to(game.player.position)
            )
            enemy_bullet_x = closest_enemy_bullet.position.x
            enemy_bullet_y = closest_enemy_bullet.position.y

        else:
            enemy_bullet_x = -1
            enemy_bullet_y = -1

        if game.enemies:
            closest_enemy = min(
                game.enemies,
                key=lambda enemy: enemy.position.distance_to(game.player.position)
            )

            enemy_x = closest_enemy.position.x
            enemy_y = closest_enemy.position.y
        else:
            enemy_x = -1
            enemy_y = -1

        return (
            player_x,
            player_y,
            enemy_x,
            enemy_y,
            enemy_bullet_x,
            enemy_bullet_y,
            bullet_x,
            bullet_y
        )

    def discretize(self, coordinate, size):
        return min(
            self.zones -1,
            int(coordinate / size * self.zones)
        )


    def get_state(self, game):
        observation = self.get_observation(game)

        player_x, player_y, enemy_x, enemy_y, enemy_bullet_x, enemy_bullet_y, bullet_x, bullet_y = observation

        player_x = self.discretize(player_x, WIDTH)
        player_y = self.discretize(player_y, HEIGHT)

        if enemy_x == -1:
            enemy_x = -1
            enemy_y = -1
        else:
            enemy_x = self.discretize(enemy_x, WIDTH)
            enemy_y = self.discretize(enemy_y, HEIGHT)


        if enemy_bullet_x == -1:
            enemy_bullet_x = -1
            enemy_bullet_y = -1
        else:
            enemy_bullet_x = self.discretize(enemy_bullet_x, WIDTH)
            enemy_bullet_y = self.discretize(enemy_bullet_y, HEIGHT)

        if bullet_x == -1:
            bullet_x = -1
            bullet_y = -1
        else:
            bullet_x = self.discretize(bullet_x, WIDTH)
            bullet_y = self.discretize(bullet_y, HEIGHT)

        return (
            player_x,
            player_y,
            enemy_x,
            enemy_y,
            enemy_bullet_x,
            enemy_bullet_y,
            bullet_x,
            bullet_y
        )
    