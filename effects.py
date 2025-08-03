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

class Shockwave(pygame.sprite.Sprite):
    def __init__(self, x, y, max_radius, lifetime, color):
        super().__init__()
        self.x = x
        self.y = y
        self.max_radius = max_radius
        self.lifetime = lifetime
        self.start_lifetime = lifetime
        self.color = color
        self.current_radius = 0
        self.image = pygame.Surface((self.max_radius * 2, self.max_radius * 2), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def update(self):
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()
            return

        progress = 1 - (self.lifetime / self.start_lifetime)
        self.current_radius = int(self.max_radius * progress)
        
        # Create a new surface each frame to handle changing alpha
        self.image = pygame.Surface((self.max_radius * 2, self.max_radius * 2), pygame.SRCALPHA)
        alpha = int(255 * (1 - progress))
        
        pygame.draw.circle(self.image, (*self.color, alpha), (self.max_radius, self.max_radius), self.current_radius, 3)
        self.rect = self.image.get_rect(center=(self.x, self.y))


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
    
    # Add the shockwave
    shockwave = Shockwave(x, y, AOE_ATTACK_RADIUS, 30, RED)
    particles_group.add(shockwave)