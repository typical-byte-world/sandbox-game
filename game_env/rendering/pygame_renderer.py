import pygame

from agents.neural_agent import NeuralAgent
from game_env.config.display import (
    BACKGROUND_COLOR,
    HEIGHT,
    WIDTH,
)
from game_env.rendering.hud.ai_debug import AIDebug
from game_env.rendering.hud.hud import HUD
from game_env.rendering.scenery.city import City


class PygameRenderer:
    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))

        pygame.display.set_caption("Space Invaders AI")

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

        self.draw_hitboxes(env)

        pygame.display.flip()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

        return True

    def close(self):
        pygame.quit()


    def draw_hitboxes(self, env):
        entities = (
            [env.player]
            + env.enemies
            + env.bullets
            + env.enemy_bullets
        )

        if env.boss is not None:
            entities.append(env.boss)

        for entity in entities:
            pygame.draw.rect(
                self.screen,
                (255, 60, 60),
                entity.rect,
                width=1,
            )

            pygame.draw.circle(
                self.screen,
                (255, 220, 0),
                (
                    int(entity.position.x),
                    int(entity.position.y),
                ),
                3,
            )