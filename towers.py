import pygame
from settings import *
import math
import assets
from effects import create_explosion, create_frost_effect, create_storm_effect


class Tower(pygame.sprite.Sprite):
    def __init__(self, pos, cost, range, damage, fire_rate):
        super().__init__()
        self.pos = pos
        self.cost = cost
        self.range = range
        self.damage = damage
        self.fire_rate = fire_rate
        self.level = 1
        self.upgrade_cost = int(cost * 1.5)
        self.last_shot_time = 0
        self.image = None # Will be set by subclasses
        self.rect = pygame.Rect(pos[0] - 25, pos[1] - 25, 50, 50) # Default rect
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
    
    def draw_vfx(self, surface, offset, overcharge_timer=0):
        # Draw disable effect if active
        if self.disable_timer > 0:
            disable_surface = pygame.Surface((50, 50), pygame.SRCALPHA)
            pygame.draw.line(disable_surface, (255, 0, 0, 200), (0, 0), (50, 50), 5)
            pygame.draw.line(disable_surface, (255, 0, 0, 200), (50, 0), (0, 50), 5)
            surface.blit(disable_surface, (self.rect.left + offset[0], self.rect.top + offset[1]))

        # Draw overcharge effect
        if overcharge_timer > 0:
            pulse = (math.sin(pygame.time.get_ticks() * 0.02) + 1) / 2 # 0 to 1
            radius = self.rect.width // 2 + int(pulse * 5)
            alpha = 50 + int(pulse * 100)
            
            overcharge_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(overcharge_surface, (255, 255, 0, alpha), (radius, radius), radius)
            surface.blit(overcharge_surface, (self.rect.centerx - radius + offset[0], self.rect.centery - radius + offset[1]))

    def get_target(self, enemies):
        closest_enemy = None
        min_dist = self.range
        for enemy in enemies:
            dist = math.hypot(self.rect.centerx - enemy.rect.centerx, self.rect.centery - enemy.rect.centery)
            if dist < min_dist:
                min_dist = dist
                closest_enemy = enemy
        return closest_enemy

    def upgrade(self):
        self.level += 1
        self.damage = int(self.damage * 1.5)
        self.range = int(self.range * 1.1)
        self.cost += self.upgrade_cost
        self.upgrade_cost = int(self.upgrade_cost * 1.5)

class SunfireSpire(Tower):
    def __init__(self, pos):
        super().__init__(pos, SUNFIRE_SPIRE_COST, SUNFIRE_SPIRE_RANGE, SUNFIRE_SPIRE_DAMAGE, SUNFIRE_SPIRE_FIRE_RATE)
        # self.image = pygame.image.load(assets.TOWER_SUNFIRE_SPIRE).convert_alpha()
        self.image = assets.get_placeholder_surface(50, 50, ORANGE)
        self.rect = self.image.get_rect(center=pos)
        self.locked_target = None
        # self.fire_sound = pygame.mixer.Sound(assets.SFX_TOWER_FIRE_SUNFIRE)
        self.fire_sound = None

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
        if self.fire_sound:
            self.fire_sound.play()
        target.take_damage(self.damage * damage_multiplier, self)
        create_explosion(target.rect.centerx, target.rect.centery, particles)
        self.vfx_timer = 15 # Longer beam
        self.target = target

    def draw_vfx(self, surface, offset, overcharge_timer=0):
        super().draw_vfx(surface, offset, overcharge_timer)
        if self.vfx_timer > 0 and self.target:
            start_pos = (self.rect.centerx + offset[0], self.rect.centery + offset[1])
            end_pos = (self.target.rect.centerx + offset[0], self.target.rect.centery + offset[1])
            pygame.draw.line(surface, ORANGE, start_pos, end_pos, 3)

class FrostSpire(Tower):
    def __init__(self, pos):
        super().__init__(pos, FROST_SPIRE_COST, FROST_SPIRE_RANGE, FROST_SPIRE_DAMAGE, FROST_SPIRE_FIRE_RATE)
        # self.image = pygame.image.load(assets.TOWER_FROST_SPIRE).convert_alpha()
        self.image = assets.get_placeholder_surface(50, 50, LIGHT_BLUE)
        self.rect = self.image.get_rect(center=pos)
        # self.fire_sound = pygame.mixer.Sound(assets.SFX_TOWER_FIRE_FROST)
        self.fire_sound = None

    def attack(self, target, enemies, projectiles, particles, screen, damage_multiplier=1.0):
        if self.fire_sound:
            self.fire_sound.play()
        # No damage, only slow
        target.speed = target.original_speed * FROST_SPIRE_SLOW_FACTOR
        target.slow_timer = FROST_SPIRE_SLOW_DURATION
        target.image.fill(LIGHT_BLUE)
        create_frost_effect(target.rect.centerx, target.rect.centery, particles)
        self.vfx_timer = 5 # Shorter beam duration
        self.target = target

    def draw_vfx(self, surface, offset, overcharge_timer=0):
        super().draw_vfx(surface, offset, overcharge_timer)
        if self.vfx_timer > 0 and self.target:
            # Draw a frozen area circle instead of a beam
            radius = 30
            overlay = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(overlay, (173, 216, 230, 75), (radius, radius), radius) # Light blue, semi-transparent
            draw_pos = (self.target.rect.centerx - radius + offset[0], self.target.rect.centery - radius + offset[1])
            surface.blit(overlay, draw_pos)

class StormSpire(Tower):
    def __init__(self, pos):
        super().__init__(pos, STORM_SPIRE_COST, STORM_SPIRE_RANGE, STORM_SPIRE_DAMAGE, STORM_SPIRE_FIRE_RATE)
        # self.image = pygame.image.load(assets.TOWER_STORM_SPIRE).convert_alpha()
        self.image = assets.get_placeholder_surface(50, 50, PURPLE)
        self.rect = self.image.get_rect(center=pos)
        self.targets_hit = []
        # self.fire_sound = pygame.mixer.Sound(assets.SFX_TOWER_FIRE_STORM)
        self.fire_sound = None

    def update(self, enemies, projectiles, particles, screen, damage_multiplier=1.0):
        # VFX update
        if self.vfx_timer > 0:
            self.vfx_timer -= 1

        # Storm Spire doesn't need a single target, it attacks all in range.
        now = pygame.time.get_ticks()
        if now - self.last_shot_time > self.fire_rate:
            self.last_shot_time = now
            # Check if any enemy is in range to justify an attack
            if self.get_target(enemies):
                self.attack(None, enemies, projectiles, particles, screen, damage_multiplier)

    def attack(self, target, enemies, projectiles, particles, screen, damage_multiplier=1.0):
        self.vfx_timer = 15 # Lightning duration
        self.targets_hit.clear()

        if self.fire_sound:
            self.fire_sound.play()

        # Find all targets in range and damage them
        for enemy in list(enemies):
            if enemy.alive() and math.hypot(self.rect.centerx - enemy.rect.centerx, self.rect.centery - enemy.rect.centery) < self.range:
                enemy.take_damage(self.damage * damage_multiplier, self)
                self.targets_hit.append(enemy)
                create_storm_effect(enemy.rect.centerx, enemy.rect.centery, particles)

    def draw_vfx(self, surface, offset, overcharge_timer=0):
        super().draw_vfx(surface, offset, overcharge_timer)
        if self.vfx_timer > 0:
            for target in self.targets_hit:
                if target.alive():
                    self.draw_lightning_bolt(surface, self.rect.center, target.rect.center, offset)

    def draw_lightning_bolt(self, surface, start_pos, end_pos, offset):
        import random
        
        start = (start_pos[0] + offset[0], start_pos[1] + offset[1])
        end = (end_pos[0] + offset[0], end_pos[1] + offset[1])

        points = []
        points.append(start)
        
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        dist = math.hypot(dx, dy)
        if dist == 0: return

        num_segments = int(dist / 15)
        if num_segments < 2: num_segments = 2

        for i in range(1, num_segments):
            progress = i / num_segments
            pos = (start[0] + dx * progress, start[1] + dy * progress)
            offset_val = random.uniform(-10, 10)
            perp_dx = -dy / dist
            perp_dy = dx / dist
            points.append((pos[0] + offset_val * perp_dx, pos[1] + offset_val * perp_dy))
        
        points.append(end)
        
        # Fade the lightning over its duration
        alpha = int(255 * (self.vfx_timer / 15.0))
        color = (255, 255, 255, alpha)
        
        pygame.draw.aalines(surface, color, False, points, 2)