import pygame

from game_env.settings import WIDTH, HEIGHT


class HUD:
    def __init__(self):
        self.font = pygame.font.Font(None, 36)

    def draw(self, screen, stats):
        score = self.font.render(
            f"SCORE  {stats.score}",
            True,
            (255, 255, 255),
        )

        wave = self.font.render(
            f"WAVE  {stats.wave}",
            True,
            (255, 255, 255),
        )

        lives = self.font.render(
            f"LIVES  {stats.lives}",
            True,
            (255, 255, 255),
        )

        screen.blit(score, (WIDTH * 0.1, 25))

        screen.blit(
            wave,
            # (WIDTH // 2 - wave.get_width() // 2, 25),
            (WIDTH * 0.5, 25)
        )

        screen.blit(
            lives,
            (WIDTH * 0.9, 25)
            # (WIDTH // 2 - lives.get_width() - 30, 25),
        )
        # screen.blit(lives, (800, 25))

        if stats.game_complete:
            title = self.font.render(
                "ALL WAVES COMPLETE",
                True,
                (255, 255, 255),
            )

            restart = self.font.render(
                "PRESS R TO RESTART",
                True,
                (180, 180, 180),
            )

            screen.blit(
                title,
                (
                    WIDTH // 2 - title.get_width() // 2,
                    HEIGHT // 2 - 40,
                ),
            )

            screen.blit(
                restart,
                (
                    WIDTH // 2 - restart.get_width() // 2,
                    HEIGHT // 2 + 20,
                ),
            )

            return


    def draw_game_over(self, screen, stats):
        title_font = pygame.font.Font(None, 96)
        font = pygame.font.Font(None, 48)

        title = title_font.render(
            "GAME OVER",
            True,
            (255, 255, 255),
        )

        score = font.render(
            f"SCORE  {stats.score}",
            True,
            (255, 255, 255),
        )

        survival = font.render(
            f"SURVIVED  {stats.survival_time:.1f}s",
            True,
            (255, 255, 255),
        )

        kills = font.render(
            f"KILLS  {stats.kills}",
            True,
            (255, 255, 255),
        )

        restart = font.render(
            "R  -  RESTART",
            True,
            (255, 255, 255),
        )

        screen.blit(
            title,
            (
                WIDTH // 2 - title.get_width() // 2,
                600,
            ),
        )

        screen.blit(
            score,
            (
                WIDTH // 2 - score.get_width() // 2,
                750,
            ),
        )

        screen.blit(
            survival,
            (
                WIDTH // 2 - survival.get_width() // 2,
                810,
            ),
        )

        screen.blit(
            kills,
            (
                WIDTH // 2 - kills.get_width() // 2,
                870,
            ),
        )

        screen.blit(
            restart,
            (
                WIDTH // 2 - restart.get_width() // 2,
                1000,
            ),
        )