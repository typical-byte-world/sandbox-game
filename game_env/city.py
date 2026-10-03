from game_env.building import Building
from game_env.settings import HEIGHT, BUILDING_HEIGHT

class City:
    def __init__(self):
        self.buildings = []

        building = Building(building_width=100, building_height=300, gap_x=4, gap_y=4,
                            window_width=5, window_height=8, building_position_x=100, building_position_y=int(HEIGHT - BUILDING_HEIGHT),
                            building_color=(150, 20, 135, 70), window_color=(20, 150, 35, 70))
        
        building2 = Building(building_width=100, building_height=300, gap_x=4, gap_y=4,
                            window_width=5, window_height=8, building_position_x=600, building_position_y=600,
                            building_color=(150, 20, 135, 70), window_color=(20, 150, 35, 70))

        self.buildings.append(building)
        self.buildings.append(building2)



    def draw(self, screen):

        for building in self.buildings:
            building.draw(screen)