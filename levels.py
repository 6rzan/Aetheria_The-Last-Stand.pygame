import pygame
from settings import *

LEVEL_1_MAP = {
    "path": [(0, 100), (200, 100), (200, 300), (400, 300), (400, 100), (600, 100), (600, 400), (800, 400), (800, 200), (1000, 200), (1000, 500), (1280, 500)],
    "initial_tower_spots": [(100, 200), (500, 250)],
    "purchasable_tower_spots": [(300, 200), (700, 300), (900, 350)],
    "barricade_spots": [(200, 150), (400, 250), (600, 200), (800, 300), (1000, 350)],
    "background_colors": (GREEN, BROWN)
}

LEVEL_2_MAP = {
    "path": [(0, 360), (150, 360), (150, 150), (400, 150), (400, 500), (700, 500), (700, 250), (1000, 250), (1000, 600), (1280, 600)],
    "initial_tower_spots": [(100, 250), (550, 350)],
    "purchasable_tower_spots": [(300, 300), (850, 400), (1100, 450)],
    "barricade_spots": [(150, 250), (400, 300), (700, 400), (1000, 400)],
    "background_colors": (DARK_BLUE, PURPLE)
}

LEVEL_3_MAP = {
    "path": [(0, 50), (1280, 50)],
    "initial_tower_spots": [(100, 150), (1180, 150)],
    "purchasable_tower_spots": [(300, 150), (500, 150), (700, 150), (900, 150)],
    "barricade_spots": [],
    "background_colors": (BLACK, WHITE)
}

ALL_LEVELS = [
    {
        "name": "Level 1",
        "difficulty": "Easy",
        "starting_volatile_currency": 300,
        "map_data": LEVEL_1_MAP
    },
    {
        "name": "Level 2",
        "difficulty": "Normal",
        "starting_volatile_currency": 200,
        "map_data": LEVEL_2_MAP
    },
    {
        "name": "Level 3",
        "difficulty": "Hard",
        "starting_volatile_currency": 150,
        "map_data": LEVEL_3_MAP
    }
]

class Level:
    def __init__(self, level_data):
        self.path = level_data["path"]
        self.initial_tower_spots = level_data["initial_tower_spots"]
        self.purchasable_tower_spots = level_data["purchasable_tower_spots"]
        self.barricade_spots = level_data.get("barricade_spots", [])
        self.background_colors = level_data["background_colors"]
        self.width = 1280 # Assuming fixed size for now
        self.height = 720

    def draw(self, screen, offset):
        # The background will be drawn by the main game loop now
        # to handle centering.
        for i in range(len(self.path) - 1):
            start_pos = (self.path[i][0] + offset[0], self.path[i][1] + offset[1])
            end_pos = (self.path[i+1][0] + offset[0], self.path[i+1][1] + offset[1])
            pygame.draw.line(screen, self.background_colors[1], start_pos, end_pos, 40)