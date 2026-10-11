import csv
from collections import deque
from pathlib import Path

import numpy as np
import torch


class TrajectoryDebugger:
    def __init__(self, output_dir, last_steps=30):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.last_steps = last_steps
        self.history = deque(maxlen=last_steps)

    def reset(self):
        self.history.clear()

    def record(self, env, agent, state, action, step):
        player = env.player

        targets = list(env.enemies)
        if env.boss is not None:
            targets.append(env.boss)

        target = None

        if targets:
            target = min(
                targets,
                key=lambda obj: abs(obj.position.x - player.position.x),
            )

        q_values = [float("nan")] * 4

        if hasattr(agent, "policy_network"):
            state_tensor = torch.as_tensor(
                np.asarray(state, dtype=np.float32),
                dtype=torch.float32,
                device=agent.device,
            ).unsqueeze(0)

            with torch.no_grad():
                q_values = agent.policy_network(state_tensor).squeeze(0).cpu().tolist()

        row = {
            "step": step,
            "player_x": float(player.position.x),
            "player_y": float(player.position.y),
            "velocity_x": float(player.velocity.x),
            "velocity_y": float(player.velocity.y),
            "target_type": (type(target).__name__ if target is not None else ""),
            "target_x": (float(target.position.x) if target is not None else ""),
            "target_y": (float(target.position.y) if target is not None else ""),
            "dx": (
                float(target.position.x - player.position.x)
                if target is not None
                else ""
            ),
            "action": str(action),
            "q_idle": q_values[0],
            "q_left": q_values[1],
            "q_right": q_values[2],
            "q_shoot": q_values[3],
        }

        self.history.append(row)

    def save(self, episode):
        if not self.history:
            return None

        path = self.output_dir / (f"stagnation_episode_{episode}.csv")

        with path.open(
            "w",
            newline="",
            encoding="utf-8",
        ) as file:
            writer = csv.DictWriter(
                file,
                fieldnames=list(self.history[0].keys()),
            )

            writer.writeheader()
            writer.writerows(self.history)

        return path
