import pygame
from settings import *
import assets
import math

LEVEL_1_MAP = {
    "path": [(0, 200), (350, 200), (350, 500), (650, 500), (650, 200), (950, 200), (950, 600), (1280, 600)],
    "initial_tower_spots": [(200, 350), (800, 350)],
    "purchasable_tower_spots": [(500, 350), (1100, 450)],
    "barricade_spots": [(350, 280), (650, 430), (950, 280)],
    "background_colors": (GREEN, BROWN)
}

LEVEL_2_MAP = {
    "path": [(0, 450), (300, 450), (300, 150), (600, 150), (600, 650), (900, 650), (900, 250), (1280, 250)],
    "initial_tower_spots": [(450, 500), (1050, 500)],
    "purchasable_tower_spots": [(450, 50), (750, 500), (1150, 500)],
    "barricade_spots": [(300, 250), (600, 350), (900, 400), (1100, 450)],
    "background_colors": (DARK_BLUE, PURPLE)
}

LEVEL_3_MAP = {
    "path": [(0, 250), (1280, 250)],
    "initial_tower_spots": [(200, 450), (1080, 450)],
    "purchasable_tower_spots": [(450, 450), (640, 450), (830, 450)],
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
        self.background_image = pygame.transform.scale(pygame.image.load(assets.GROUND_TILE).convert(), (self.width, self.height))
        self.path_tile = pygame.transform.scale(pygame.image.load(assets.PATH_TILE).convert_alpha(), (PATH_WIDTH, PATH_WIDTH))

    def draw(self, surface, offset):
        # The background is now drawn in the main game loop for responsive scaling

        # Draw the colored path shape
        for i in range(len(self.path) - 1):
            start = pygame.math.Vector2(self.path[i])
            end = pygame.math.Vector2(self.path[i+1])
            pygame.draw.line(surface, self.background_colors[1], start + offset, end + offset, PATH_WIDTH + 20)

        # Tile the path texture on top
        for i in range(len(self.path) - 1):
            start = pygame.math.Vector2(self.path[i])
            end = pygame.math.Vector2(self.path[i+1])
            
            length = (end - start).length()
            if length == 0: continue
            direction = (end - start).normalize()
            
            for j in range(0, int(length), self.path_tile.get_width()):
                pos = start + direction * j
                tile_rect = self.path_tile.get_rect(center = pos + offset)
                surface.blit(self.path_tile, tile_rect)