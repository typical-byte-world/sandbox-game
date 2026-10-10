
import pygame

from game_env.settings import (
    BACKGROUND_COLOR,
    WIDTH,
    HEIGHT,
)

from game_env.city import City
from game_env.hud.hud import HUD
from game_env.hud.ai_debug import AIDebug
from game_env.agent.NeuralAgent import NeuralAgent


class PygameRenderer:
    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode(
            (WIDTH, HEIGHT)
        )

        pygame.display.set_caption(
            "Space Invaders AI"
        )

        self.city = City()
        self.hud = HUD()
        self.ai_debug = AIDebug()

    def render(self, env, agent=None):
        self.screen.fill(BACKGROUND_COLOR)

        self.city.draw(self.screen)

        # Player
        env.player.draw(self.screen)

        # Player bullets
        for bullet in env.bullets:
            bullet.draw(self.screen)

        # Enemies
        for enemy in env.enemies:
            enemy.draw(self.screen)

        # Boss
        if env.boss:
            env.boss.draw(self.screen)

        # Enemy bullets
        for bullet in env.enemy_bullets:
            bullet.draw(self.screen)

        # HUD
        if env.game_over:
            self.hud.draw_game_over(
                self.screen,
                env.stats,
            )
        else:
            self.hud.draw(
                self.screen,
                env.stats,
            )

        # AI Debug
        if isinstance(agent, NeuralAgent):
            self.ai_debug.draw(
                self.screen,
                agent,
            )

        pygame.display.flip()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

        return True

    def close(self):
        pygame.quit()
