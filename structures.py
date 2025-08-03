import pygame
from settings import *

class Barricade(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.pos = pos
        self.health = BARRICADE_HEALTH
        self.max_health = BARRICADE_HEALTH
        self.lifetime = BARRICADE_DURATION
        self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
        # Main block
        pygame.draw.rect(self.image, BROWN, (2, 2, 36, 36))
        # High-contrast border
        pygame.draw.rect(self.image, (255, 255, 0, 200), (0, 0, 40, 40), 2)
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
        self.image = pygame.Surface((50, 50), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (0, 50, 0, 100), (25, 25), 25)
        pygame.draw.circle(self.image, (255, 255, 255, 120), (25, 25), 25, 2)
        self.rect = self.image.get_rect(center=pos)
        self.is_occupied = False