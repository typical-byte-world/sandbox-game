

class Observation:
    def get_observation(self, game):
        player_x = game.player.position.x
        player_y = game.player.position.y

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
        )