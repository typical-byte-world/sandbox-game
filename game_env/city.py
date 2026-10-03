from game_env.building import Building
from game_env.settings import (
    HEIGHT,
    WIDTH,
    BUILDING_HEIGHT,
    AMOUNT_OF_BUILDINGS,
    MIN_BUILDING_WIDTH,
    MAX_BUILDING_WIDTH,
    MIN_BUILDING_HEIGHT,
    MAX_BUILDING_HEIGHT,
    MIN_GAP,
    MAX_GAP,
    MIN_WINDOW_WIDTH,
    MAX_WINDOW_WIDTH,
    MIN_WINDOW_HEIGHT,
    MAX_WINDOW_HEIGHT,
    CITY_ALPHA
)
import random
import pygame



class City:
    def __init__(self):
        self.buildings = []

        self.amount_of_buildings = AMOUNT_OF_BUILDINGS
        self.generate_buildings()

    def generate_buildings(self):
        for _ in range(self.amount_of_buildings):

            building_height = random.randint(MIN_BUILDING_HEIGHT, MAX_BUILDING_HEIGHT)

            self.buildings.append(
                Building(
                    building_width=random.randint(MIN_BUILDING_WIDTH, MAX_BUILDING_WIDTH),
                    building_height=building_height,
                    gap_x=random.randint(MIN_GAP, MAX_GAP),
                    gap_y=random.randint(MIN_GAP, MAX_GAP),
                    window_width=random.randint(MIN_WINDOW_WIDTH, MAX_WINDOW_WIDTH),
                    window_height=random.randint(MIN_WINDOW_HEIGHT, MAX_WINDOW_HEIGHT),
                    building_position_x=random.randint(0, WIDTH),
                    building_position_y=HEIGHT-building_height,
                    building_color=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255), 255),
                    window_color=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255), 255)
                )
            )

        


    def draw(self, screen):
        city_surface = pygame.Surface(
            (WIDTH, HEIGHT),
            pygame.SRCALPHA
        )
        for building in self.buildings:
            building.draw(city_surface)

        city_surface.set_alpha(CITY_ALPHA)

        screen.blit(city_surface, [0, 0])
        