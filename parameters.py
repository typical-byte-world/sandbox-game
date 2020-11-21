class colors:
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GRAY = (125, 125, 125)
    LIGHT_BLUE = (64, 128, 255)
    GREEN = (0, 200, 64)
    YELLOW = (225, 225, 0)
    PINK = (230, 50, 230)
    RED = (255, 0, 0)
    BLUE = (0, 0, 255)
    PURPLE = (139, 0, 139)


class settings:
    screen_height = 1000
    screen_width = 1680

    FPS = 60
    spaceship_path = 'imgs/hiclipart.com.png'
    SPRITE_PADDING = 20  # in pixels

    bullet_path = 'imgs/bullet.png'
    bullet_padding = 50
    bullet_width = 5
    bullet_height = 20
    bullets_allowed = 5

    alien_path = 'imgs/alien.png'
    alien_size = (100, 100)
    alien_start_position = 100

    alien_speed_y = 25

    LEFT = 1
    RIGHT = -1

    button_width = 400
    button_height = 100
    button_font_size = 32

    # dynamic settings
    def __init__(self):
        self.alien_speed = 5
        self.bullet_speed = 10
        self.spaceship_move_speed = 15

        # multiplied factor
        self.multiplied_factor = 1.5

    def increase_speed(self):
        self.alien_speed = self.alien_speed * self.multiplied_factor
        self.bullet_speed = self.bullet_speed * self.multiplied_factor
        self.spaceship_move_speed = self.spaceship_move_speed * self.multiplied_factor
