import pygame
from settings import *
import assets

class Barricade(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.pos = pos
        self.health = BARRICADE_HEALTH
        self.max_health = BARRICADE_HEALTH
        self.lifetime = BARRICADE_DURATION
        self.image = pygame.Surface(BARRICADE_SIZE, pygame.SRCALPHA)
        # Main block
        pygame.draw.rect(self.image, BROWN, (2, 2, BARRICADE_SIZE[0] - 4, BARRICADE_SIZE[1] - 4))
        # High-contrast border
        pygame.draw.rect(self.image, (255, 255, 0, 200), (0, 0, BARRICADE_SIZE[0], BARRICADE_SIZE[1]), 2)
        self.rect = self.image.get_rect(center=pos)

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.kill()

    def update(self):
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()

class SpirePlot(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.pos = pos
        self.image = pygame.transform.scale(pygame.image.load(assets.TOWER_PLOT).convert_alpha(), PLOT_SIZE)
        self.rect = self.image.get_rect(center=pos)
        self.is_occupied = False