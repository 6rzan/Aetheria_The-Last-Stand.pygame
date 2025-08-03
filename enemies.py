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
        self.last_hit_by = None
        self.attack_timer = 0

    def take_damage(self, amount, tower):
        self.health -= amount
        self.last_hit_by = tower

    def update(self, particles, barricades):
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

class ShieldingSentinel(Enemy):
    def __init__(self, path):
        super().__init__(SHIELDING_SENTINEL_HEALTH, SHIELDING_SENTINEL_SPEED, SHIELDING_SENTINEL_VALUE, path, DARK_BLUE)
        self.shield = SHIELDING_SENTINEL_SHIELD
        self.max_shield = SHIELDING_SENTINEL_SHIELD
        self.shield_cooldown = 0

    def take_damage(self, amount, tower):
        self.shield_cooldown = SHIELDING_SENTINEL_COOLDOWN
        if self.shield > 0:
            damage_to_shield = min(self.shield, amount)
            self.shield -= damage_to_shield
            remaining_damage = amount - damage_to_shield
            if remaining_damage > 0:
                super().take_damage(remaining_damage, tower)
        else:
            super().take_damage(amount, tower)

    def update(self, particles, barricades):
        super().update(particles, barricades)
        if self.shield_cooldown > 0:
            self.shield_cooldown -= 1
        elif self.shield < self.max_shield:
            self.shield += 1 # Regenerate shield slowly

        # Shield visual
        if self.shield > 0:
            shield_surface = pygame.Surface((self.rect.width + 6, self.rect.height + 6), pygame.SRCALPHA)
            pygame.draw.rect(shield_surface, (0, 191, 255, 150), shield_surface.get_rect(), 3, border_radius=5)
            self.image.blit(shield_surface, (-3, -3))
        else:
            # Redraw the base image in case the shield visual was blitted on top
            self.image.fill(self.original_color)

class ChronoWarper(Enemy):
    def __init__(self, path):
        super().__init__(CHRONO_WARPER_HEALTH, CHRONO_WARPER_SPEED, CHRONO_WARPER_VALUE, path, PURPLE)
        self.pulse_timer = CHRONO_WARPER_PULSE_RATE
        self.pulse_vfx_timer = 0

    def update(self, particles, barricades):
        super().update(particles, barricades)
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
        super().__init__(SABOTEUR_HEALTH, SABOTEUR_SPEED, SABOTEUR_VALUE, path, BROWN)

    def kill(self):
        if self.last_hit_by:
            self.last_hit_by.disable_timer = SABOTEUR_DISABLE_DURATION
        super().kill()