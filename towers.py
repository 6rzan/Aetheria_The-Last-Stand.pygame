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
        self.slow_effect_timer = 0
        self.disable_timer = 0

    def update(self, enemies, projectiles, particles, screen, damage_multiplier=1.0):
        # VFX update
        if self.vfx_timer > 0:
            self.vfx_timer -= 1
        else:
            if hasattr(self, 'target') and self.target:
                self.target = None

        # Handle disable effect
        if self.disable_timer > 0:
            self.disable_timer -= 1
            # The visual effect is now handled in draw_vfx
            return # Do not attack if disabled

        # Handle slow effect
        current_fire_rate = self.fire_rate
        if self.slow_effect_timer > 0:
            self.slow_effect_timer -= 1
            current_fire_rate *= (1 / CHRONO_WARPER_SLOW_FACTOR)

        # Attack logic
        now = pygame.time.get_ticks()
        if now - self.last_shot_time > current_fire_rate:
            self.last_shot_time = now
            self.target = self.get_target(enemies)
            if self.target:
                self.attack(self.target, enemies, projectiles, particles, screen, damage_multiplier)

        self.projectiles.update()
    
    def draw_vfx(self, screen):
        # Draw disable effect if active
        if self.disable_timer > 0:
            disable_surface = pygame.Surface((50, 50), pygame.SRCALPHA)
            pygame.draw.line(disable_surface, (255, 0, 0, 200), (0, 0), (50, 50), 5)
            pygame.draw.line(disable_surface, (255, 0, 0, 200), (50, 0), (0, 50), 5)
            screen.blit(disable_surface, self.rect.topleft)

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
        self.locked_target = None

    def update(self, enemies, projectiles, particles, screen, damage_multiplier=1.0):
        # Sunfire Spire specific update for target locking
        if self.vfx_timer > 0:
            self.vfx_timer -= 1
        else:
            self.target = None

        # Check if locked target is still valid
        if self.locked_target and self.locked_target.alive():
            dist = math.hypot(self.rect.centerx - self.locked_target.rect.centerx, self.rect.centery - self.locked_target.rect.centery)
            if dist > self.range:
                self.locked_target = None # Target out of range
        else:
            self.locked_target = None # Target is dead

        # If no locked target, find a new one
        if not self.locked_target:
            self.locked_target = self.get_target(enemies)

        # Attack logic
        now = pygame.time.get_ticks()
        if self.locked_target and now - self.last_shot_time > self.fire_rate:
            self.last_shot_time = now
            self.attack(self.locked_target, enemies, projectiles, particles, screen, damage_multiplier)

    def attack(self, target, enemies, projectiles, particles, screen, damage_multiplier=1.0):
        target.take_damage(self.damage * damage_multiplier, self)
        create_explosion(target.rect.centerx, target.rect.centery, particles)
        self.vfx_timer = 15 # Longer beam
        self.target = target

    def draw_vfx(self, screen):
        super().draw_vfx(screen)
        if self.vfx_timer > 0 and self.target:
            pygame.draw.line(screen, ORANGE, self.rect.center, self.target.rect.center, 3)

class FrostSpire(Tower):
    def __init__(self, pos):
        super().__init__(pos, FROST_SPIRE_COST, FROST_SPIRE_RANGE, FROST_SPIRE_DAMAGE, FROST_SPIRE_FIRE_RATE)
        self.image.fill(LIGHT_BLUE)

    def attack(self, target, enemies, projectiles, particles, screen, damage_multiplier=1.0):
        # No damage, only slow
        target.speed = target.original_speed * FROST_SPIRE_SLOW_FACTOR
        target.slow_timer = FROST_SPIRE_SLOW_DURATION
        target.image.fill(LIGHT_BLUE)
        create_frost_effect(target.rect.centerx, target.rect.centery, particles)
        self.vfx_timer = 5 # Shorter beam duration
        self.target = target

    def draw_vfx(self, screen):
        super().draw_vfx(screen)
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
        self.secondary_targets = []

    def attack(self, target, enemies, projectiles, particles, screen, damage_multiplier=1.0):
        self.vfx_timer = 15 # Lightning duration
        self.target = target
        self.secondary_targets.clear()

        # Find all targets in AOE
        for enemy in list(enemies):
            if enemy.alive() and math.hypot(target.rect.centerx - enemy.rect.centerx, target.rect.centery - enemy.rect.centery) < STORM_SPIRE_AOE_RADIUS:
                if enemy is not target:
                    self.secondary_targets.append(enemy)
                enemy.take_damage(self.damage * damage_multiplier, self)
                create_storm_effect(enemy.rect.centerx, enemy.rect.centery, particles)

    def draw_vfx(self, screen):
        super().draw_vfx(screen)
        if self.vfx_timer > 0 and self.target:
            # Draw main lightning bolt to primary target
            self.draw_lightning_bolt(screen, self.rect.center, self.target.rect.center)
            # Draw branching lightning to secondary targets
            for secondary in self.secondary_targets:
                if secondary.alive():
                    self.draw_lightning_bolt(screen, self.target.rect.center, secondary.rect.center)

    def draw_lightning_bolt(self, screen, start_pos, end_pos):
        import random
        points = []
        points.append(start_pos)
        
        dx = end_pos[0] - start_pos[0]
        dy = end_pos[1] - start_pos[1]
        dist = math.hypot(dx, dy)
        if dist == 0: return

        num_segments = int(dist / 15)
        if num_segments < 2: num_segments = 2

        for i in range(1, num_segments):
            progress = i / num_segments
            pos = (start_pos[0] + dx * progress, start_pos[1] + dy * progress)
            offset = random.uniform(-10, 10)
            perp_dx = -dy / dist
            perp_dy = dx / dist
            points.append((pos[0] + offset * perp_dx, pos[1] + offset * perp_dy))
        
        points.append(end_pos)
        
        # Fade the lightning over its duration
        alpha = int(255 * (self.vfx_timer / 15.0))
        color = (255, 255, 255, alpha)
        
        if pygame.SRCALPHA:
            temp_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            pygame.draw.aalines(temp_surface, color, False, points, 2)
            screen.blit(temp_surface, (0,0))
        else:
            pygame.draw.aalines(screen, (255,255,255), False, points, 2)