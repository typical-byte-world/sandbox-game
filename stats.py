import pygame


class Stats:
    def __init__(self, settings):
        self.settings = settings
        self.score = 0
        self.flots = 0

    def reset_score(self):
        self.score = 0

    def killed_alien(self):
        self.score += 1

    def killed_flots(self):
        self.flots += 1