
"""Read-only diagnostics of DQN behavior."""

import csv
from collections import deque
from pathlib import Path

import numpy as np
import torch


class TrajectoryDebugger:
    def __init__(
        self,
        output_dir,
        last_steps=30,
        tremor_window=8,
        tremor_reversals=6,
    ):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.last_steps = last_steps
        self.history = deque(maxlen=last_steps)

        self.tremor_window = tremor_window
        self.tremor_reversals = tremor_reversals

        self.action_window = deque(maxlen=tremor_window)

        self.life_events = 0
        self.tremor_events = 0

        self._last_tremor_step = -10**9

    def reset(self):
        self.history.clear()
        self.action_window.clear()

        self.life_events = 0
        self.tremor_events = 0

        self._last_tremor_step = -10**9

    @staticmethod
    def _bullet_threat(env):
        """
        Estimate collision time using relative velocity.

        Assumes constant velocity for both objects.
        Used only for diagnostics, not for agent decisions.
        """
        player = env.player

        px = float(player.position.x)
        py = float(player.position.y)

        pvx = float(player.velocity.x)
        pvy = float(player.velocity.y)

        candidates = []

        for bullet in env.enemy_bullets:
            bx = float(bullet.position.x)
            by = float(bullet.position.y)

            vx = float(bullet.velocity.x) - pvx
            vy = float(bullet.velocity.y) - pvy

            dx = bx - px
            dy = by - py

            hx = (player.rect.width + bullet.rect.width) / 2
            hy = (player.rect.height + bullet.rect.height) / 2

            t_enter = float("-inf")
            t_exit = float("inf")

            for d, v, h in (
                (dx, vx, hx),
                (dy, vy, hy),
            ):
                if abs(v) < 1e-9:
                    if abs(d) > h:
                        t_enter = float("inf")
                        t_exit = float("-inf")
                        break
                else:
                    t1 = (-h - d) / v
                    t2 = (h - d) / v

                    t_enter = max(t_enter, min(t1, t2))
                    t_exit = min(t_exit, max(t1, t2))

            if t_enter <= t_exit and t_exit >= 0:
                ttc = max(0.0, t_enter)
            else:
                ttc = None

            distance_sq = dx * dx + dy * dy

            candidates.append(
                (ttc, distance_sq, dx, dy, vx, vy)
            )

        if not candidates:
            return {
                "bullet_dx": "",
                "bullet_dy": "",
                "bullet_relative_vx": "",
                "bullet_relative_vy": "",
                "time_to_impact_s": "",
                "projected_collision": False,
                "enemy_bullet_count": 0,
            }

        # Prefer earliest predicted collision.
        # If none exists, use the nearest bullet.
        best = min(
            candidates,
            key=lambda c: (
                c[0] is None,
                c[0] if c[0] is not None else float("inf"),
                c[1],
            ),
        )

        ttc, _, dx, dy, vx, vy = best

        return {
            "bullet_dx": dx,
            "bullet_dy": dy,
            "bullet_relative_vx": vx,
            "bullet_relative_vy": vy,
            "time_to_impact_s": "" if ttc is None else ttc,
            "projected_collision": ttc is not None,
            "enemy_bullet_count": len(candidates),
        }

    def record(self, env, agent, state, action, step):
        player = env.player

        targets = list(env.enemies)

        if env.boss is not None:
            targets.append(env.boss)

        target = None

        if targets:
            target = min(
                targets,
                key=lambda obj: abs(
                    obj.position.x - player.position.x
                ),
            )

        q_values = [float("nan")] * len(agent.actions)

        if hasattr(agent, "policy_network"):
            state_tensor = torch.as_tensor(
                np.asarray(state, dtype=np.float32),
                dtype=torch.float32,
                device=agent.device,
            ).unsqueeze(0)

            with torch.no_grad():
                q_values = (
                    agent.policy_network(state_tensor)
                    .squeeze(0)
                    .cpu()
                    .tolist()
                )

        action_index = agent.actions.index(action)

        action_names = (
            "IDLE",
            "LEFT",
            "RIGHT",
            "SHOOT",
        )

        if len(agent.actions) == 4:
            action_name = action_names[action_index]
        else:
            action_name = str(action)

        row = {
            "step": step,
            "lives_before": int(env.stats.lives),
            "lives_after": "",
            "life_lost": False,
            "player_x": float(player.position.x),
            "player_y": float(player.position.y),
            "velocity_x": float(player.velocity.x),
            "velocity_y": float(player.velocity.y),
            "target_type": (
                type(target).__name__
                if target is not None
                else ""
            ),
            "target_x": (
                float(target.position.x)
                if target is not None
                else ""
            ),
            "target_y": (
                float(target.position.y)
                if target is not None
                else ""
            ),
            "dx": (
                float(
                    target.position.x - player.position.x
                )
                if target is not None
                else ""
            ),
            "action": action_name,
            "q_idle": q_values[0],
            "q_left": q_values[1],
            "q_right": q_values[2],
            "q_shoot": q_values[3],
            "q_left_minus_right": (
                q_values[1] - q_values[2]
            ),
            **self._bullet_threat(env),
        }

        self.history.append(row)
        self.action_window.append(action_name)

    def after_step(self, env, episode):
        """
        Called immediately after env.step().

        Detects:
        - life loss
        - rapid LEFT/RIGHT reversals
        """
        if not self.history:
            return []

        row = self.history[-1]

        row["lives_after"] = int(env.stats.lives)

        row["life_lost"] = (
            row["lives_after"] < row["lives_before"]
        )

        paths = []

        # Life loss
        if row["life_lost"]:
            self.life_events += 1

            path = self.save(
                episode,
                kind="life_loss",
                number=self.life_events,
            )

            if path is not None:
                paths.append(path)

        # Tremor detection
        if len(self.action_window) == self.tremor_window:
            actions = list(self.action_window)

            reversals = sum(
                a != b and {a, b} == {"LEFT", "RIGHT"}
                for a, b in zip(actions, actions[1:])
            )

            if (
                reversals >= self.tremor_reversals
                and row["step"] - self._last_tremor_step
                >= self.tremor_window
            ):
                self.tremor_events += 1
                self._last_tremor_step = row["step"]

                path = self.save(
                    episode,
                    kind="tremor",
                    number=self.tremor_events,
                )

                if path is not None:
                    paths.append(path)

        return paths

    def save(
        self,
        episode,
        kind="stagnation",
        number=None,
    ):
        if not self.history:
            return None

        suffix = (
            f"_{number}"
            if number is not None
            else ""
        )

        path = (
            self.output_dir
            / f"{kind}_episode_{episode}{suffix}.csv"
        )

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
