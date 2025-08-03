# assets.py

# This file centralizes all asset paths for the game.
# It is designed to be imported by other modules, providing a single source of truth for asset locations.
# The asset loading code is currently commented out and replaced with placeholders to maintain functionality.

import pygame
import os

# --- BASE PATHS ---
# It's good practice to build absolute paths from the script's location
# to avoid issues with the current working directory.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')

# --- DIRECTORY PATHS ---
IMAGES_DIR = os.path.join(ASSETS_DIR, 'images')
SOUNDS_DIR = os.path.join(ASSETS_DIR, 'sounds')
MUSIC_DIR = os.path.join(ASSETS_DIR, 'music')
FONTS_DIR = os.path.join(ASSETS_DIR, 'fonts')
UI_DIR = os.path.join(IMAGES_DIR, 'ui')

# --- IMAGE ASSETS ---

# Backgrounds
BG_MAIN_MENU = os.path.join(IMAGES_DIR, 'bg_main_menu.png')
BG_LEVEL_1 = os.path.join(IMAGES_DIR, 'bg_level_1.png')
BG_LEVEL_2 = os.path.join(IMAGES_DIR, 'bg_level_2.png')

# Towers
TOWER_SUNFIRE_SPIRE = os.path.join(IMAGES_DIR, 'tower_sunfire_spire.png')
TOWER_FROST_SPIRE = os.path.join(IMAGES_DIR, 'tower_frost_spire.png')
TOWER_STORM_SPIRE = os.path.join(IMAGES_DIR, 'tower_storm_spire.png')

# Enemies
ENEMY_SHADOW_CRAWLER = os.path.join(IMAGES_DIR, 'enemy_shadow_crawler.png')
ENEMY_SHADOW_FLYER = os.path.join(IMAGES_DIR, 'enemy_shadow_flyer.png')
ENEMY_SHIELDING_SENTINEL = os.path.join(IMAGES_DIR, 'enemy_shielding_sentinel.png')
ENEMY_CHRONO_WARPER = os.path.join(IMAGES_DIR, 'enemy_chrono_warper.png')
ENEMY_SABOTEUR = os.path.join(IMAGES_DIR, 'enemy_saboteur.png')
ENEMY_HEALER = os.path.join(IMAGES_DIR, 'enemy_healer.png')

# Projectiles
PROJECTILE_SUNFIRE = os.path.join(IMAGES_DIR, 'projectile_sunfire.png')
PROJECTILE_FROST = os.path.join(IMAGES_DIR, 'projectile_frost.png')
PROJECTILE_STORM = os.path.join(IMAGES_DIR, 'projectile_storm.png')

# UI Elements
UI_BUTTON_START = os.path.join(UI_DIR, 'button_start.png')
UI_HEART_ICON = os.path.join(UI_DIR, 'heart_icon.png')
UI_GOLD_ICON = os.path.join(UI_DIR, 'gold_icon.png')
UI_PAUSE_BUTTON = os.path.join(UI_DIR, 'pause_button.png')
UI_FAST_FORWARD_BUTTON = os.path.join(UI_DIR, 'fast_forward_button.png')
UI_SETTINGS_BUTTON = os.path.join(UI_DIR, 'settings_button.png')
CASTLE_IMAGE = os.path.join(IMAGES_DIR, 'castle.png')


# --- SOUND EFFECTS ---
SFX_TOWER_FIRE_SUNFIRE = os.path.join(SOUNDS_DIR, 'sfx_tower_fire_sunfire.wav')
SFX_TOWER_FIRE_FROST = os.path.join(SOUNDS_DIR, 'sfx_tower_fire_frost.wav')
SFX_TOWER_FIRE_STORM = os.path.join(SOUNDS_DIR, 'sfx_tower_fire_storm.wav')
SFX_ENEMY_HIT = os.path.join(SOUNDS_DIR, 'sfx_enemy_hit.wav')
SFX_ENEMY_DEATH = os.path.join(SOUNDS_DIR, 'sfx_enemy_death.wav')
SFX_UI_CLICK = os.path.join(SOUNDS_DIR, 'sfx_ui_click.wav')

# --- MUSIC ---
MUSIC_MAIN_MENU = os.path.join(MUSIC_DIR, 'music_main_menu.mp3')
MUSIC_LEVEL_1 = os.path.join(MUSIC_DIR, 'music_level_1.mp3')

# --- FONTS ---
FONT_PRIMARY = os.path.join(FONTS_DIR, 'primary_font.ttf')
FONT_TITLE = os.path.join(FONTS_DIR, 'title_font.ttf')

# --- PLACEHOLDER SURFACES ---
# These are used to keep the game runnable without the actual assets.
# They can be replaced with actual image loading code once the assets are available.

def get_placeholder_surface(width, height, color):
    """Creates a simple colored surface."""
    surface = pygame.Surface((width, height))
    surface.fill(color)
    return surface

# Example of how to use placeholders:
# self.image = get_placeholder_surface(32, 32, (255, 0, 0)) # Red square for an enemy
# self.rect = self.image.get_rect()