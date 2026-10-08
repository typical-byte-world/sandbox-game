import pygame


DEBUG_ALPHA = 40


class AIDebug:
    def __init__(self):
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)

    def draw(self, screen, agent):
        data = agent.get_debug_data()

        observation = data["observation"]
        q_values = data["q_values"]
        hidden = data["hidden"]

        weights1 = data["weights1"]
        weights2 = data["weights2"]

        gradient_weights1 = data["gradient_weights1"]
        gradient_weights2 = data["gradient_weights2"]

        history = data["history"]

        q_before_update = data["q_before_update"]
        target_q = data["target_q"]
        q_after_update = data["q_after_update"]

        right_x = 1050

        self._draw_graph(
            screen,
            history.rewards,
            20,
            20,
            330,
            150,
            "REWARD",
        )

        self._draw_graph(
            screen,
            history.losses,
            360,
            20,
            330,
            150,
            "LOSS",
        )

        self._draw_graph(
            screen,
            history.max_q_values,
            700,
            20,
            330,
            150,
            "MAX Q",
        )

        title = self.font.render(
            "AI DEBUG",
            True,
            (255, 255, 255),
        )

        screen.blit(
            title,
            (right_x, 20),
        )

        self._draw_policy(
            screen,
            data["epsilon"],
            data["exploration"],
            right_x,
            55,
        )

        self._draw_training_step(
            screen,
            q_before_update,
            target_q,
            q_after_update,
            right_x,
            125,
        )

        if observation is not None:
            self._draw_observation(
                screen,
                observation,
                right_x,
                225,
            )

        self._draw_q_values(
            screen,
            q_values,
            data["actions"],
            data["action_index"],
            right_x,
            480,
        )

        self._draw_hidden(
            screen,
            hidden,
            right_x,
            850,
        )

        self._draw_weights(
            screen,
            weights1,
            20,
            210,
            "WEIGHTS 1",
        )

        self._draw_weights(
            screen,
            weights2,
            530,
            210,
            "WEIGHTS 2",
        )

        self._draw_weights(
            screen,
            gradient_weights1,
            20,
            450,
            "GRADIENTS 1",
        )

        self._draw_weights(
            screen,
            gradient_weights2,
            530,
            450,
            "GRADIENTS 2",
        )

    def _draw_policy(
        self,
        screen,
        epsilon,
        exploration,
        x,
        y,
    ):
        label = self.small_font.render(
            "POLICY",
            True,
            (200, 200, 200),
        )

        screen.blit(
            label,
            (x, y),
        )

        epsilon_text = self.small_font.render(
            f"epsilon = {epsilon:.3f}",
            True,
            (220, 220, 220),
        )

        screen.blit(
            epsilon_text,
            (x, y + 22),
        )

        mode = (
            "EXPLORATION"
            if exploration
            else "EXPLOITATION"
        )

        mode_color = (
            (255, 180, 80)
            if exploration
            else (120, 220, 120)
        )

        mode_text = self.small_font.render(
            f"mode = {mode}",
            True,
            mode_color,
        )

        screen.blit(
            mode_text,
            (x, y + 44),
        )

    def _draw_training_step(
        self,
        screen,
        q_before,
        target,
        q_after,
        x,
        y,
    ):
        label = self.small_font.render(
            "TRAINING STEP",
            True,
            (200, 200, 200),
        )

        screen.blit(
            label,
            (x, y),
        )

        values = [
            ("Q BEFORE", q_before),
            ("TARGET", target),
            ("Q AFTER", q_after),
        ]

        for i, (name, value) in enumerate(values):
            row_y = y + 20 + i * 22

            text = self.small_font.render(
                f"{name:12} {value:8.4f}",
                True,
                (220, 220, 220),
            )

            screen.blit(
                text,
                (x, row_y),
            )

    def _draw_observation(
        self,
        screen,
        observation,
        x,
        y,
    ):
        label = self.small_font.render(
            "OBSERVATION",
            True,
            (200, 200, 200),
        )

        screen.blit(
            label,
            (x, y),
        )

        names = [
            "player_x",
            "player_y",
            "bullet_present",
            "bullet_dx",
            "bullet_dy",
            "enemy_present",
            "enemy_dx",
            "enemy_dy",
            "enemy_bullet",
            "enemy_bullet_dx",
            "enemy_bullet_dy",
        ]

        max_abs = max(
            max(abs(float(value)) for value in observation),
            0.001,
        )

        for i, value in enumerate(observation):
            row_y = y + 25 + i * 20

            value = float(value)

            text = self.small_font.render(
                f"{names[i]:18} {value:7.3f}",
                True,
                (220, 220, 220),
            )

            screen.blit(
                text,
                (x, row_y),
            )

            bar_width = int(
                abs(value) / max_abs * 100
            )

            self._draw_transparent_rect(
                screen,
                (
                    80,
                    180,
                    255,
                    DEBUG_ALPHA,
                ),
                (
                    x + 180,
                    row_y + 2,
                    bar_width,
                    8,
                ),
            )

    def _draw_q_values(
        self,
        screen,
        q_values,
        actions,
        selected_action_index,
        x,
        y,
    ):
        label = self.small_font.render(
            "Q-VALUES / ACTIONS",
            True,
            (200, 200, 200),
        )

        screen.blit(
            label,
            (x, y),
        )

        max_abs = max(
            max(abs(float(value)) for value in q_values),
            0.001,
        )

        for i, value in enumerate(q_values):
            row_y = y + 25 + i * 20

            value = float(value)
            action = actions[i]

            shoot = "S" if action.shoot else "-"

            action_text = (
                f"{action.move_x:+d},"
                f"{action.move_y:+d},"
                f"{shoot}"
            )

            if i == selected_action_index:
                text_color = (255, 220, 80)
            else:
                text_color = (220, 220, 220)

            text = self.small_font.render(
                f"{i:02d} [{action_text}] {value:7.3f}",
                True,
                text_color,
            )

            screen.blit(
                text,
                (x, row_y),
            )

            bar_width = int(
                abs(value) / max_abs * 150
            )

            self._draw_transparent_rect(
                screen,
                (
                    80,
                    180,
                    255,
                    DEBUG_ALPHA,
                ),
                (
                    x + 145,
                    row_y + 2,
                    bar_width,
                    10,
                ),
            )

    def _draw_hidden(
        self,
        screen,
        hidden,
        x,
        y,
    ):
        label = self.small_font.render(
            "HIDDEN ACTIVATIONS",
            True,
            (200, 200, 200),
        )

        screen.blit(
            label,
            (x, y),
        )

        for i, value in enumerate(hidden):
            cell_x = x + (i % 8) * 70
            cell_y = y + 30 + (i // 8) * 30

            value = max(
                0.0,
                min(float(value), 1.0),
            )

            brightness = int(
                value * 255
            )

            self._draw_transparent_rect(
                screen,
                (
                    brightness,
                    brightness,
                    brightness,
                    DEBUG_ALPHA,
                ),
                (
                    cell_x,
                    cell_y,
                    50,
                    20,
                ),
            )

            text = self.small_font.render(
                str(i),
                True,
                (255, 0, 0),
            )

            screen.blit(
                text,
                (
                    cell_x + 20,
                    cell_y + 2,
                ),
            )

    def _draw_graph(
        self,
        screen,
        values,
        x,
        y,
        width,
        height,
        title,
    ):
        if not values:
            return

        surface = pygame.Surface(
            (width, height),
            pygame.SRCALPHA,
        )

        pygame.draw.rect(
            surface,
            (
                25,
                25,
                25,
                DEBUG_ALPHA,
            ),
            (
                0,
                0,
                width,
                height,
            ),
        )

        screen.blit(
            surface,
            (x, y),
        )

        title_surface = self.small_font.render(
            title,
            True,
            (200, 200, 200),
        )

        screen.blit(
            title_surface,
            (x + 5, y + 5),
        )

        minimum = min(values)
        maximum = max(values)

        if maximum == minimum:
            maximum += 1

        points = []

        for i, value in enumerate(values):
            px = (
                x
                + (
                    i
                    / max(len(values) - 1, 1)
                )
                * width
            )

            normalized = (
                (value - minimum)
                / (maximum - minimum)
            )

            py = (
                y
                + height
                - normalized
                * (height - 25)
            )

            points.append(
                (px, py)
            )

        if len(points) > 1:
            pygame.draw.lines(
                screen,
                (80, 180, 255),
                False,
                points,
                2,
            )

        min_text = self.small_font.render(
            f"{minimum:.4f}",
            True,
            (140, 140, 140),
        )

        max_text = self.small_font.render(
            f"{maximum:.4f}",
            True,
            (140, 140, 140),
        )

        screen.blit(
            min_text,
            (
                x + 5,
                y + height - 20,
            ),
        )

        screen.blit(
            max_text,
            (
                x + 5,
                y + 25,
            ),
        )

    def _draw_weights(
        self,
        screen,
        weights,
        x,
        y,
        title,
    ):
        if weights is None:
            return

        label = self.small_font.render(
            title,
            True,
            (200, 200, 200),
        )

        screen.blit(
            label,
            (x, y),
        )

        rows, columns = weights.shape

        cell_width = 20
        cell_height = 12

        max_abs = max(
            abs(float(weights.min())),
            abs(float(weights.max())),
            0.001,
        )

        for row in range(rows):
            for column in range(columns):
                value = float(
                    weights[row, column]
                )

                normalized = value / max_abs

                if normalized >= 0:
                    intensity = int(
                        normalized * 255
                    )

                    color = (
                        intensity,
                        intensity,
                        intensity,
                        DEBUG_ALPHA,
                    )
                else:
                    intensity = int(
                        abs(normalized) * 255
                    )

                    color = (
                        intensity,
                        0,
                        0,
                        DEBUG_ALPHA,
                    )

                cell_x = (
                    x
                    + column * cell_width
                )

                cell_y = (
                    y
                    + 25
                    + row * cell_height
                )

                self._draw_transparent_rect(
                    screen,
                    color,
                    (
                        cell_x,
                        cell_y,
                        cell_width - 1,
                        cell_height - 1,
                    ),
                )

    def _draw_transparent_rect(
        self,
        screen,
        color,
        rect,
    ):
        surface = pygame.Surface(
            (
                rect[2],
                rect[3],
            ),
            pygame.SRCALPHA,
        )

        pygame.draw.rect(
            surface,
            color,
            (
                0,
                0,
                rect[2],
                rect[3],
            ),
        )

        screen.blit(
            surface,
            (
                rect[0],
                rect[1],
            ),
        )