import pygame
from settings import *
from effects import create_dissolve_effect

class Enemy(pygame.sprite.Sprite):
    def __init__(self, health, speed, value, path, color):
        super().__init__()
        self.health = health
        self.max_health = health
        self.speed = speed
        self.original_speed = speed
        self.value = value
        self.path = path
        self.path_index = 0
        self.pos = list(self.path[self.path_index])
        self.original_color = color
        self.image = pygame.Surface((30, 30)) # Placeholder
        self.image.fill(self.original_color)
        self.rect = self.image.get_rect(center=self.pos)
        self.slow_timer = 0

    def update(self, particles):
        if self.health <= 0:
            print(f"Enemy at {self.pos} has died.")
            create_dissolve_effect(self.rect.centerx, self.rect.centery, particles)
            # pygame.mixer.Sound('assets/enemy_squish.wav').play()
            self.kill()
            return

        if self.slow_timer > 0:
            self.slow_timer -= 1
            if self.slow_timer == 0:
                self.speed = self.original_speed
                self.image.fill(self.original_color)

        if self.path_index < len(self.path) - 1:
            target = self.path[self.path_index + 1]
            dx = target[0] - self.pos[0]
            dy = target[1] - self.pos[1]
            dist = (dx**2 + dy**2)**0.5
            if dist > self.speed:
                self.pos[0] += dx / dist * self.speed
                self.pos[1] += dy / dist * self.speed
            else:
                self.pos = list(target)
                self.path_index += 1
            self.rect.center = self.pos
        else:
            # pygame.mixer.Sound('assets/heartcrystal_crack.wav').play()
            self.kill() # Reached the end of the path

class ShadowCrawler(Enemy):
    def __init__(self, path):
        super().__init__(SHADOW_CRAWLER_HEALTH, SHADOW_CRAWLER_SPEED, SHADOW_CRAWLER_VALUE, path, GREY)

class ShadowFlyer(Enemy):
    def __init__(self, path):
        super().__init__(SHADOW_FLYER_HEALTH, SHADOW_FLYER_SPEED, SHADOW_FLYER_VALUE, path, WHITE)