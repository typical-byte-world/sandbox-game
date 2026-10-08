from game_env.entities.bosses.boss import Boss
from game_env.settings import WIDTH

class WaveManager:
    WAVES = [
        {
            "color": (180, 180, 180),
            "enemies": {
                "scout": 5,
                "shooter": 5,
                "kamikaze": 5,

                # "dodger": 1,
                # "tactical": 1,
            },
        },
        # {
        #     "color": (80, 170, 255),
        #     "enemies": {
        #         "scout": 2,
        #         "shooter": 2,
        #         # "dodger": 3,
        #         "kamikaze": 5,
        #         # "tactical": 2,
        #     },
        # },
        # {
        #     "color": (255, 120, 70),
        #     "enemies": {
        #         "scout": 4,
        #         "shooter": 3,
        #         # "dodger": 4,
        #         "kamikaze": 3,
        #         # "tactical": 3,
        #     },
        # },
    ]

    def __init__(self, game):
        self.game = game
        self.game_complete = False

        self.current_wave = 0
        self.spawn_queue = []
        self.wave_color = (255, 255, 255)

    def start_next_wave(self):
        self.current_wave += 1

        if self.current_wave > len(self.WAVES):
            self.game.boss = Boss(
                WIDTH // 2,
                250,
            )

            return

        wave = self.WAVES[self.current_wave - 1]

        self.wave_color = wave["color"]
        self.spawn_queue = []

        for enemy_type, count in wave["enemies"].items():
            for _ in range(count):
                self.spawn_queue.append(enemy_type)

        self.game.stats.wave = self.current_wave

        self.spawn_next_enemy()

    def spawn_next_enemy(self):
        if not self.spawn_queue:
            return

        enemy_type = self.spawn_queue.pop(0)

        self.game.spawn_enemy(
            enemy_type,
            self.wave_color,
            self.current_wave,
        )


    def update(self, dt):
        if self.game.stats.game_complete:
            return

        if self.game.boss:
            return

        if self.game.enemies:
            return

        if self.spawn_queue:
            self.spawn_next_enemy()
            return

        self.start_next_wave()