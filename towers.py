import pygame
from settings import *
import math
from effects import create_explosion, create_frost_effect, create_storm_effect


class Tower(pygame.sprite.Sprite):
    def __init__(self, pos, cost, range, damage, fire_rate):
        super().__init__()
        self.pos = pos
        self.cost = cost
        self.range = range
        self.damage = damage
        self.fire_rate = fire_rate
        self.last_shot_time = 0
        self.image = pygame.Surface((50, 50)) # Placeholder
        self.rect = self.image.get_rect(center=pos)
        self.projectiles = pygame.sprite.Group()
        self.vfx_timer = 0
        self.vfx_duration = 0

    def update(self, enemies, projectiles, particles, screen):
        # VFX update
        if self.vfx_timer > 0:
            self.vfx_timer -= 1
        else:
            if hasattr(self, 'target') and self.target:
                self.target = None

        # Attack logic
        now = pygame.time.get_ticks()
        if now - self.last_shot_time > self.fire_rate:
            self.last_shot_time = now
            self.target = self.get_target(enemies)
            if self.target:
                self.attack(self.target, enemies, projectiles, particles, screen)

        self.projectiles.update()
    
    def draw_vfx(self, screen):
        pass # To be implemented by subclasses

    def get_target(self, enemies):
        closest_enemy = None
        min_dist = self.range
        for enemy in enemies:
            dist = math.hypot(self.rect.centerx - enemy.rect.centerx, self.rect.centery - enemy.rect.centery)
            if dist < min_dist:
                min_dist = dist
                closest_enemy = enemy
        return closest_enemy

class SunfireSpire(Tower):
    def __init__(self, pos):
        super().__init__(pos, SUNFIRE_SPIRE_COST, SUNFIRE_SPIRE_RANGE, SUNFIRE_SPIRE_DAMAGE, SUNFIRE_SPIRE_FIRE_RATE)
        self.image.fill(ORANGE)

    def attack(self, target, enemies, projectiles, particles, screen):
        target.health -= self.damage
        create_explosion(target.rect.centerx, target.rect.centery, particles)
        self.vfx_timer = 15 # Longer beam
        self.target = target

    def draw_vfx(self, screen):
        if self.vfx_timer > 0 and self.target:
            pygame.draw.line(screen, ORANGE, self.rect.center, self.target.rect.center, 3)

class FrostSpire(Tower):
    def __init__(self, pos):
        super().__init__(pos, FROST_SPIRE_COST, FROST_SPIRE_RANGE, FROST_SPIRE_DAMAGE, FROST_SPIRE_FIRE_RATE)
        self.image.fill(LIGHT_BLUE)

    def attack(self, target, enemies, projectiles, particles, screen):
        # No damage, only slow
        target.speed = target.original_speed * FROST_SPIRE_SLOW_FACTOR
        target.slow_timer = FROST_SPIRE_SLOW_DURATION
        target.image.fill(LIGHT_BLUE)
        create_frost_effect(target.rect.centerx, target.rect.centery, particles)
        self.vfx_timer = 5 # Shorter beam duration
        self.target = target

    def draw_vfx(self, screen):
        if self.vfx_timer > 0 and self.target:
            # Draw a frozen area circle instead of a beam
            radius = 30
            overlay = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(overlay, (173, 216, 230, 75), (radius, radius), radius) # Light blue, semi-transparent
            screen.blit(overlay, (self.target.rect.centerx - radius, self.target.rect.centery - radius))

class StormSpire(Tower):
    def __init__(self, pos):
        super().__init__(pos, STORM_SPIRE_COST, STORM_SPIRE_RANGE, STORM_SPIRE_DAMAGE, STORM_SPIRE_FIRE_RATE)
        self.image.fill(PURPLE)

    def attack(self, target, enemies, projectiles, particles, screen):
        self.vfx_timer = 20 # Slower pulse
        self.target = target  # Store target for VFX
        for enemy in list(enemies):
            if enemy.alive() and math.hypot(target.rect.centerx - enemy.rect.centerx, target.rect.centery - enemy.rect.centery) < STORM_SPIRE_AOE_RADIUS:
                enemy.health -= self.damage
                create_storm_effect(enemy.rect.centerx, enemy.rect.centery, particles)

    def draw_vfx(self, screen):
        if self.vfx_timer > 0 and self.target:
            # Pulsing AOE effect
            pulse_progress = self.vfx_timer / 20.0 # Match the new timer
            
            # Radius grows and then shrinks
            current_radius = int(STORM_SPIRE_AOE_RADIUS * math.sin(pulse_progress * math.pi))
            
            # Alpha fades out
            alpha = int(200 * (1 - (1-pulse_progress)**2))

            if current_radius > 0:
                overlay = pygame.Surface((current_radius * 2, current_radius * 2), pygame.SRCALPHA)
                
                # Fill
                pygame.draw.circle(overlay, (128, 0, 128, alpha), (current_radius, current_radius), current_radius)
                # Border
                pygame.draw.circle(overlay, (255, 255, 255, alpha), (current_radius, current_radius), current_radius, 3)
                
                screen.blit(overlay, (self.target.rect.centerx - current_radius, self.target.rect.centery - current_radius))