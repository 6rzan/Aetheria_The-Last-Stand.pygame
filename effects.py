import pygame
import random
from settings import *

class Particle(pygame.sprite.Sprite):
    def __init__(self, x, y, color, lifetime):
        super().__init__()
        self.x = x
        self.y = y
        self.color = color
        self.lifetime = lifetime
        self.size = random.randint(2, 5)
        self.image = pygame.Surface((self.size, self.size))
        self.image.fill(self.color)
        self.rect = self.image.get_rect(center=(self.x, self.y))
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-2, 2)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.rect.center = (self.x, self.y)
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()

def create_explosion(x, y, particles_group):
    for _ in range(20):
        color = random.choice([ORANGE, YELLOW])
        particle = Particle(x, y, color, random.randint(20, 40))
        particles_group.add(particle)

def create_dissolve_effect(x, y, particles_group):
    for _ in range(15):
        particle = Particle(x, y, GREY, random.randint(10, 30))
        particles_group.add(particle)

def create_frost_effect(x, y, particles_group):
    for _ in range(15):
        color = random.choice([LIGHT_BLUE, WHITE])
        particle = Particle(x, y, color, random.randint(15, 35))
        particles_group.add(particle)

def create_storm_effect(x, y, particles_group):
    # Lightning sparks
    for _ in range(10):
        color = random.choice([WHITE, YELLOW])
        particle = Particle(x, y, color, random.randint(10, 20))
        particle.vx = random.uniform(-4, 4)
        particle.vy = random.uniform(-4, 4)
        particle.size = random.randint(1, 3)
        particles_group.add(particle)

def create_aoe_explosion(x, y, particles_group):
    # A bigger, more impactful explosion
    for _ in range(50):
        color = random.choice([RED, ORANGE, YELLOW])
        particle = Particle(x, y, color, random.randint(30, 60))
        particle.vx = random.uniform(-5, 5)
        particle.vy = random.uniform(-5, 5)
        particles_group.add(particle)