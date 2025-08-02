import pygame
from settings import *

LEVEL_1_MAP = {
    "path": [(0, 100), (200, 100), (200, 300), (400, 300), (400, 100), (600, 100), (600, 400), (800, 400), (800, 200), (1000, 200), (1000, 500), (1280, 500)],
    "tower_spots": [(100, 200), (300, 200), (500, 250), (700, 300), (900, 350)],
    "background_colors": (GREEN, BROWN)
}

LEVEL_2_MAP = {
    "path": [(0, 360), (150, 360), (150, 150), (400, 150), (400, 500), (700, 500), (700, 250), (1000, 250), (1000, 600), (1280, 600)],
    "tower_spots": [(100, 250), (300, 300), (550, 350), (850, 400), (1100, 450)],
    "background_colors": (DARK_BLUE, PURPLE)
}

class Level:
    def __init__(self, level_data):
        self.path = level_data["path"]
        self.tower_spots = level_data["tower_spots"]
        self.background_colors = level_data["background_colors"]

    def draw(self, screen):
        screen.fill(self.background_colors[0])
        # Draw a different color for the path area for contrast
        for i in range(len(self.path) - 1):
            pygame.draw.line(screen, self.background_colors[1], self.path[i], self.path[i+1], 40)
        
        # Draw tower spots
        for spot in self.tower_spots:
            pygame.draw.circle(screen, (0, 50, 0, 100), spot, 25) # Dark green placeholder