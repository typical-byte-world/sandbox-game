import pygame

from agents.dqn_agent import DQNAgent
from game_env.core.simple_target import SimpleTargetEnv

WIDTH = 900
HEIGHT = 240
FPS = 8

MODEL_PATH = "models/simple-target/dqn/dqn_n5.pt"

env = SimpleTargetEnv(max_steps=100)

agent = DQNAgent(
    input_size=2,
    training=False,
    n_steps=5,
)
agent.load(MODEL_PATH)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("DQN — Simple Target")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 26)

running = True
episode = 0

while running:
    state, info = env.reset(seed=10000 + episode)
    terminated = False
    truncated = False
    steps = 0
    total_reward = 0.0

    while running and not (terminated or truncated):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if not running:
            break

        player_x = float(state[0]) * 100
        target_x = float(state[1]) * 100

        screen.fill((18, 20, 30))

        pygame.draw.line(
            screen,
            (90, 90, 110),
            (50, 130),
            (850, 130),
            2,
        )

        px = int(50 + player_x * 8)
        tx = int(50 + target_x * 8)

        pygame.draw.circle(
            screen,
            (80, 160, 255),
            (px, 130),
            12,
        )

        pygame.draw.circle(
            screen,
            (255, 90, 90),
            (tx, 130),
            10,
        )

        action = agent.choose_action(state)

        text = (
            f"Episode: {episode + 1}  "
            f"Step: {steps}  "
            f"Distance: {abs(target_x - player_x):.1f}  "
            f"Action: {action}"
        )

        screen.blit(
            font.render(text, True, (240, 240, 240)),
            (20, 25),
        )

        pygame.display.flip()
        clock.tick(FPS)

        (
            state,
            reward,
            terminated,
            truncated,
            info,
        ) = env.step(action)

        steps += 1
        total_reward += reward

    if running:
        print(
            f"Episode {episode + 1} | "
            f"Steps: {steps} | "
            f"Reward: {total_reward:.2f} | "
            f"Success: {info.get('success', False)}"
        )

        pygame.time.wait(500)
        episode += 1

pygame.quit()
