import pygame
from game_env.settings import (
    WIDTH,
    HEIGHT,
    BUILDING_HEIGHT,
    BUILDING_WIDTH, 
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    WINDOW_GAP_X,
    WINDOW_GAP_Y,
    BUILDING_POSITION_X,
    BUILDING_COLOR,
    WINDOW_COLOR
)
from game_env.pixel_art import draw_pixel_sprite


class Building:
    def __init__(self, building_width, building_height, gap_x, gap_y,
                       window_width, window_height,
                       building_position_x, building_position_y,
                       building_color, window_color):
        self.height = building_height
        self.width = building_width
        self.gap_x = gap_x
        self.gap_y = gap_y

        self.usable_width = building_width - gap_x * 2
        self.usable_height = building_height - gap_y * 2

        self.window_width = window_width
        self.window_height = window_height

        self.columns = self.usable_width // (self.window_width + gap_x)
        self.rows = self.usable_height // (self.window_height + gap_y)

        self.building_position_x = building_position_x
        self.building_position_y = building_position_y

        self.windows_width = self.columns * self.window_width
        self.windows_height = self.rows * self.window_height

        # X
        self.x_gaps_count = self.columns - 1
        self.gaps_width = self.x_gaps_count * gap_x
        self.grid_width = self.windows_width + self.gaps_width
        self.remaining_width = building_width - self.grid_width
        self.side_margin_x = int(self.remaining_width / 2)

        # Y
        self.y_gaps_count = self.rows - 1
        self.gaps_height = self.y_gaps_count * gap_y
        self.grid_height = self.windows_height + self.gaps_height
        self.remaining_height = building_height - self.grid_height
        self.side_margin_y = int(self.remaining_height / 2)

        self.building_color = building_color
        self.window_color = window_color

    def draw(self, screen):
        city_surface = pygame.Surface(
            (WIDTH, HEIGHT),
            pygame.SRCALPHA
        )
        pygame.draw.rect(
            city_surface,
            self.building_color,
            (  
                self.building_position_x, self.building_position_y, self.width, self.height
            )
        )

        self.draw_windows(city_surface)

        screen.blit(city_surface, [0, 0])

    def draw_windows(self, screen):

        for row in range(self.rows):
            for column in range(self.columns):

                window_y = self.building_position_y + self.side_margin_y + row * (self.window_height + self.gap_y)
                window_x = self.building_position_x + self.side_margin_x + column * (self.window_width + self.gap_x)

                pygame.draw.rect(
                    screen,
                    self.window_color,
                    (window_x, window_y, self.window_width, self.window_height)
                )