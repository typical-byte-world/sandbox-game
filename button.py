import pygame
from parameters import colors


class Button:
    def __init__(self, settings, screen, message):
        self.settings = settings
        self.screen = screen

        self.width = settings.button_width
        self.height = settings.button_height
        self.button_color = colors.GRAY
        self.text_color = colors.WHITE
        self.font = pygame.font.SysFont(None, self.settings.button_font_size)

        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = self.screen.get_rect().center
        self.prepare_message(message)

    def prepare_message(self, message):
        self.message_image = self.font.render(message, True, self.text_color, self.button_color)
        self.message_image_rect = self.message_image.get_rect()
        self.message_image_rect.center = self.rect.center

    def draw_button(self):
        self.screen.fill(self.button_color, self.rect)
        self.screen.blit(self.message_image, self.message_image_rect)
