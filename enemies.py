import pygame
import assets
from settings import *
from effects import create_dissolve_effect
import math
class Enemy(pygame.sprite.Sprite):
    def __init__(self, health, speed, value, path):
        super().__init__()
        self.health = health
        self.max_health = health
        self.speed = speed
        self.original_speed = speed
        self.value = value
        self.path = path
        self.path_index = 0
        self.pos = list(self.path[self.path_index])
        self.image = None # To be set by subclass
        self.original_image = None
        self.original_color = None
        self.rect = None # Will be created in subclass
        self.slow_timer = 0
        self.last_hit_by = None
        self.attack_timer = 0

    def take_damage(self, amount, tower, hit_sound=None):
        if hit_sound:
            hit_sound.play()
        self.health -= amount
        self.last_hit_by = tower

    def update(self, particles, barricades, all_enemies):
        # Death is now handled in the main game loop

        # Check for barricades
        blocking_barricade = None
        for barricade in barricades:
            # Check a point slightly ahead of the enemy
            look_ahead_pos = (self.pos[0] + (self.rect.width / 2), self.pos[1])
            if barricade.rect.collidepoint(look_ahead_pos):
                blocking_barricade = barricade
                break
        
        if blocking_barricade:
            # Stop and attack
            if self.attack_timer <= 0:
                blocking_barricade.take_damage(ENEMY_ATTACK_DAMAGE)
                self.attack_timer = ENEMY_ATTACK_RATE
            else:
                self.attack_timer -= 1
            return # Don't move

        if self.slow_timer > 0:
            self.slow_timer -= 1
            if self.slow_timer == 0:
                self.speed = self.original_speed
                self.image = self.original_image.copy()

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
            self.kill() # Reached the end of the path
    
    def kill(self):
        super().kill()

class ShadowCrawler(Enemy):
    def __init__(self, path):
        super().__init__(SHADOW_CRAWLER_HEALTH, SHADOW_CRAWLER_SPEED, SHADOW_CRAWLER_VALUE, path)
        self.image = pygame.transform.scale(pygame.image.load(assets.ENEMY_SHADOW_CRAWLER).convert_alpha(), SHADOW_CRAWLER_SIZE)
        self.original_color = GREY
        self.original_image = self.image.copy()
        self.rect = self.image.get_rect(center=self.pos)

class ShadowFlyer(Enemy):
    def __init__(self, path):
        super().__init__(SHADOW_FLYER_HEALTH, SHADOW_FLYER_SPEED, SHADOW_FLYER_VALUE, path)
        self.image = pygame.transform.scale(pygame.image.load(assets.ENEMY_SHADOW_FLYER).convert_alpha(), SHADOW_FLYER_SIZE)
        self.original_color = WHITE
        self.original_image = self.image.copy()
        self.rect = self.image.get_rect(center=self.pos)

class ShieldingSentinel(Enemy):
    def __init__(self, path):
        super().__init__(SHIELDING_SENTINEL_HEALTH, SHIELDING_SENTINEL_SPEED, SHIELDING_SENTINEL_VALUE, path)
        self.image_shielded = pygame.transform.scale(pygame.image.load(assets.ENEMY_SHIELDING_SENTINEL).convert_alpha(), SHIELDING_SENTINEL_SIZE)
        self.image_no_shield = pygame.transform.scale(pygame.image.load(assets.ENEMY_SHIELDING_SENTINEL_NO_SHIELD).convert_alpha(), SHIELDING_SENTINEL_SIZE)
        self.original_image = self.image_shielded.copy()
        self.image = self.image_shielded.copy()
        self.rect = self.image.get_rect(center=self.pos)
        self.shield = SHIELDING_SENTINEL_SHIELD
        self.max_shield = SHIELDING_SENTINEL_SHIELD
        self.shield_cooldown = 0

    def take_damage(self, amount, tower, hit_sound=None):
        if hit_sound:
            hit_sound.play()
        self.shield_cooldown = SHIELDING_SENTINEL_COOLDOWN
        if self.shield > 0:
            damage_to_shield = min(self.shield, amount)
            self.shield -= damage_to_shield
            if self.shield <= 0:
                self.image = self.image_no_shield.copy()
                self.original_image = self.image_no_shield.copy()
            remaining_damage = amount - damage_to_shield
            if remaining_damage > 0:
                super().take_damage(remaining_damage, tower, hit_sound=None) # Don't play sound twice
        else:
            super().take_damage(amount, tower, hit_sound)

    def update(self, particles, barricades, all_enemies):
        super().update(particles, barricades, all_enemies)
        if self.shield_cooldown > 0:
            self.shield_cooldown -= 1
        elif self.shield < self.max_shield:
            self.shield += 1 # Regenerate shield slowly
            if self.shield > 0:
                self.image = self.image_shielded.copy()
                self.original_image = self.image_shielded.copy()

class ChronoWarper(Enemy):
    def __init__(self, path):
        super().__init__(CHRONO_WARPER_HEALTH, CHRONO_WARPER_SPEED, CHRONO_WARPER_VALUE, path)
        self.image = pygame.transform.scale(pygame.image.load(assets.ENEMY_CHRONO_WARPER).convert_alpha(), CHRONO_WARPER_SIZE)
        self.original_color = PURPLE
        self.original_image = self.image.copy()
        self.rect = self.image.get_rect(center=self.pos)
        self.pulse_timer = CHRONO_WARPER_PULSE_RATE
        self.pulse_vfx_timer = 0

    def update(self, particles, barricades, all_enemies):
        super().update(particles, barricades, all_enemies)
        if self.pulse_timer > 0:
            self.pulse_timer -= 1
        
        if self.pulse_vfx_timer > 0:
            self.pulse_vfx_timer -= 1

    def can_pulse(self):
        return self.pulse_timer <= 0

    def reset_pulse_timer(self):
        self.pulse_timer = CHRONO_WARPER_PULSE_RATE
        self.pulse_vfx_timer = FPS // 2 # VFX lasts for half a second

class Saboteur(Enemy):
    def __init__(self, path):
        super().__init__(SABOTEUR_HEALTH, SABOTEUR_SPEED, SABOTEUR_VALUE, path)
        self.image = pygame.transform.scale(pygame.image.load(assets.ENEMY_SABOTEUR).convert_alpha(), SABOTEUR_SIZE)
        self.original_color = BROWN
        self.original_image = self.image.copy()
        self.rect = self.image.get_rect(center=self.pos)

    def kill(self):
        if self.last_hit_by:
            self.last_hit_by.disable_timer = SABOTEUR_DISABLE_DURATION
        super().kill()

class Healer(Enemy):
    def __init__(self, path):
        super().__init__(HEALER_HEALTH, HEALER_SPEED, HEALER_VALUE, path)
        self.image = pygame.transform.scale(pygame.image.load(assets.ENEMY_HEALER).convert_alpha(), HEALER_SIZE)
        self.original_color = GREEN
        self.original_image = self.image.copy()
        self.rect = self.image.get_rect(center=self.pos)
        self.heal_timer = HEALER_PULSE_RATE
        self.heal_vfx_timer = 0

    def update(self, particles, barricades, all_enemies):
        super().update(particles, barricades, all_enemies)
        if self.heal_timer > 0:
            self.heal_timer -= 1
        else:
            self.heal_pulse(all_enemies)
            self.heal_timer = HEALER_PULSE_RATE
            self.heal_vfx_timer = FPS // 2
        
        if self.heal_vfx_timer > 0:
            self.heal_vfx_timer -= 1

    def heal_pulse(self, all_enemies):
        for enemy in all_enemies:
            if enemy is not self and enemy.alive():
                dist = ( (self.rect.centerx - enemy.rect.centerx) ** 2 + (self.rect.centery - enemy.rect.centery) ** 2 ) ** 0.5
                if dist <= HEALER_PULSE_RADIUS:
                    enemy.health = min(enemy.max_health, enemy.health + HEALER_HEAL_AMOUNT)