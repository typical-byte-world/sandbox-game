import pygame


def draw_pixel_sprite(
    screen,
    sprite,
    position,
    pixel_size,
    color,
):
    width = len(sprite[0]) * pixel_size
    height = len(sprite) * pixel_size

    start_x = int(position.x - width / 2)
    start_y = int(position.y - height / 2)

    for row, line in enumerate(sprite):
        for column, pixel in enumerate(line):
            if pixel == "X":
                pygame.draw.rect(
                    screen,
                    color,
                    (
                        start_x + column * pixel_size,
                        start_y + row * pixel_size,
                        pixel_size,
                        pixel_size,
                    ),
                )

PLAYER_SPRITE = [
    "     XX     ",
    "    XXXX    ",
    "   XXXXXX   ",
    "  XX XX XX  ",
    " XXXXXXXXXX ",
    "XXXXXXXXXXXX",
    "XX  XXXX  XX",
    "    XXXX    ",
]


SCOUT_SPRITE = [
    "      XX      ",
    "      XX      ",
    "      XXX     ",
    "     XXXX     ",
    "     XXXX     ",
    "    XXXXXX    ",
    "   XXXXXXXX   ",
    "  X  XXXX   X",
    "  X XXXX      X",
    "     XXXX     ",
    "      XX      ",
    "      XX      ",
    "      XX      ",
    "      XX      ",
]


SHOOTER_SPRITE = [
    "...XXX...",
    "..XXXXX..",
    ".XXXXXXX.",
    "XXXXXXXXX",
    "XXXXXXXXX",
    "..XXXXX..",
    "..XXXXX..",
    ".XXXXXXX.",
    "XXXXXXXXX",
    "XXXXXXXXX",
    "...XXX...",
]


KAMIKAZE_SPRITE = [
    "...X...",
    "..XXX..",
    ".XXXXX.",
    "XXXXXXX",
    "XXXXXXX",
    ".XXXXX.",
    ".XXXXX.",
    "..XXX..",
    "..XXX..",
    ".XXXXX.",
    "XXXXXXX",
]


DODGER_SPRITE = [
    "..XXX..",
    ".XXXXX.",
    "XXXXXXX",
    "XX...XX",
    "XX...XX",
    "XXXXXXX",
    ".XXXXX.",
    "..XXX..",
]

TACTICAL_SPRITE = [
    "...XXX...",
    "..XXXXX..",
    ".XXXXXXX.",
    "XXXXXXXXX",
    "XXX........XXX",
    "XXX........XXX",
    "XXXXXXXXX",
    ".XXXXXXX.",
    "..XXXXX..",
]


BOSS_SPRITE = [
    "....XXXXX....",
    "...XXXXXXX...",
    "..XXXXXXXXX..",
    ".XXXXXXXXXXX.",
    "XXXXXXXXXXXXX",
    "XXX..XXX..XXX",
    "XXXXXXXXXXXXX",
    "XXXXXXXXXXXXX",
    ".XXXXXXXXXXX.",
    "..XXXXXXXXX..",
    "...XXXXXXX...",
    "....XXXXX....",
]