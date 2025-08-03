import pygame
import sys
import math
import json
import assets
from settings import *
import levels
from levels import Level, LEVEL_1_MAP, LEVEL_2_MAP
from towers import SunfireSpire, FrostSpire, StormSpire
from enemies import ShadowCrawler, ShadowFlyer, ShieldingSentinel, ChronoWarper, Saboteur
from effects import create_explosion, create_dissolve_effect, create_aoe_explosion
from waves import WaveManager
from structures import Barricade, SpirePlot

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Aetheria: The Last Stand")
        self.clock = pygame.time.Clock()
        self.level = Level(LEVEL_1_MAP)
        self.wave_manager = WaveManager(self.level.path)
        # self.font = pygame.font.Font(assets.FONT_PRIMARY, 36)
        self.font = pygame.font.Font(None, 36) # Fallback
        # self.title_font = pygame.font.Font(assets.FONT_TITLE, 72)
        self.title_font = pygame.font.Font(None, 72) # Fallback
        
        # --- CURRENCY & PROGRESSION REFACTOR ---
        self.meta_currency = 500 # Default value
        self.volatile_currency = 0
        self.load_progress()

        # In-run variables
        self.heartcrystal_health = 100
        self.wave_number = 0
        self.wave_timer = 5 * FPS
        self.enemies = pygame.sprite.Group()
        self.towers = pygame.sprite.Group()
        self.projectiles = pygame.sprite.Group()
        self.particles = pygame.sprite.Group()
        self.barricades = pygame.sprite.Group()
        self.spire_plots = pygame.sprite.Group()
        self.selected_tower = None
        self.selected_tower_instance = None
        self.placing_barricade = False
        self.placing_plot = False
        self.placing_aoe_attack = False
        self.overcharge_timer = 0
        self.game_state = "main_menu" # Start in the main menu
        self.is_paused = False
        self.game_speed = 1
        self.music_volume = 1.0
        self.sfx_volume = 1.0
        self.setup_level()
        self.wave_took_damage = False

        # UI Feedback timers
        self.perm_currency_fx_timer = 0
        self.temp_currency_fx_timer = 0
        self.perm_fx_color = WHITE
        self.temp_fx_color = WHITE

        # --- LOAD ASSETS ---
        self.load_assets()

        self.shop_towers = [
            {"name": "Sunfire Spire", "cost": SUNFIRE_SPIRE_COST, "type": "sunfire", "color": ORANGE, "damage": SUNFIRE_SPIRE_DAMAGE, "range": SUNFIRE_SPIRE_RANGE},
            {"name": "Frost Spire", "cost": FROST_SPIRE_COST, "type": "frost", "color": LIGHT_BLUE, "damage": "Slows", "range": FROST_SPIRE_RANGE},
            {"name": "Storm Spire", "cost": STORM_SPIRE_COST, "type": "storm", "color": PURPLE, "damage": STORM_SPIRE_DAMAGE, "range": STORM_SPIRE_RANGE},
            {"name": "Barricade", "cost": BARRICADE_COST, "type": "barricade", "color": BROWN, "damage": "Blocks", "range": "N/A"},
            {"name": "Spire Plot", "cost": SPIRE_PLOT_COST, "type": "plot", "color": DARK_BLUE, "damage": "Build on it", "range": "N/A"},
        ]

    def run(self):
        # pygame.mixer.music.load(assets.MUSIC_MAIN_MENU)
        # pygame.mixer.music.play(-1) # Loop indefinitely
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.VIDEORESIZE:
                    self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                
                if self.game_state == "playing":
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1: # Left-click
                            self.handle_mouse_click(event.pos)
                        elif event.button == 3: # Right-click
                            self.set_placing_state(None) # Universal cancel
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_p:
                            self.toggle_pause()
                elif self.game_state in ["game_over", "win"]:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r:
                            self.game_state = "main_menu"
                elif self.game_state == "main_menu":
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            self.game_state = "level_select"
                elif self.game_state == "settings":
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1:
                            self.handle_settings_click(event.pos)
                elif self.game_state == "level_select":
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1:
                            self.handle_level_select_click(event.pos)

            if self.game_state == "playing":
                if not self.is_paused:
                    self.update()
                self.draw()
                if self.is_paused:
                    self.draw_pause_menu()
            elif self.game_state == "game_over":
                self.draw_game_over()
            elif self.game_state == "win":
                self.draw_win_screen()
            elif self.game_state == "main_menu":
                self.draw_main_menu()
            elif self.game_state == "level_select":
                self.draw_level_select_menu()
            elif self.game_state == "settings":
                self.draw_settings_menu()

            pygame.display.flip()
            self.clock.tick(FPS * self.game_speed)

        pygame.quit()
        sys.exit()

    def update(self):
        if self.game_state != "playing":
            return
        
        if self.overcharge_timer > 0:
            self.overcharge_timer -= 1
        damage_multiplier = OVERCHARGE_MULTIPLIER if self.overcharge_timer > 0 else 1.0
        
        self.enemies.update(self.particles, self.barricades, self.enemies)
        self.towers.update(self.enemies, self.projectiles, self.particles, self.screen, damage_multiplier)
        self.particles.update()
        
        self.handle_wave_spawning()
        self.check_collisions()
        self.handle_enemy_deaths()
        self.handle_enemy_abilities()
        self.check_win_loss()

    def draw(self):
        self.screen.fill(BLACK)

        # --- Centered Map Drawing ---
        # Calculate the offset to center the map
        map_width, map_height = self.level.width, self.level.height
        offset_x = (self.screen.get_width() - map_width) // 2
        offset_y = (self.screen.get_height() - map_height) // 2
        camera_offset = (offset_x, offset_y)

        # Create a temporary surface for the game world
        game_surface = pygame.Surface((self.screen.get_width(), self.screen.get_height()), pygame.SRCALPHA)

        self.level.draw(game_surface, camera_offset)
        
        # Adjust drawing positions for all game objects
        for group in [self.spire_plots, self.enemies, self.towers, self.barricades, self.particles]:
            for sprite in group:
                new_rect = sprite.rect.move(camera_offset)
                game_surface.blit(sprite.image, new_rect)

        # Draw Castle
        if self.level.path:
            end_pos = self.level.path[-1]
            castle_rect = self.castle_image.get_rect(center=(end_pos[0] + offset_x, end_pos[1] + offset_y))
            game_surface.blit(self.castle_image, castle_rect)

        for tower in self.towers:
            tower.draw_vfx(game_surface, camera_offset, self.overcharge_timer)

        self.screen.blit(game_surface, (0,0))

        self.draw_left_hud()
        self.draw_right_shop()
        
        if self.selected_tower or self.placing_barricade or self.placing_plot:
            self.draw_placement_grid()
            self.draw_ghost_tower()
        elif self.placing_aoe_attack:
            self.draw_ghost_aoe()
            
        self.draw_enemy_abilities()

    def draw_left_hud(self):
        panel_width = 250
        hud_panel = pygame.Surface((panel_width, self.screen.get_height()), pygame.SRCALPHA)
        hud_panel.fill((20, 20, 20, 180)) # Semi-transparent dark panel
        self.screen.blit(hud_panel, (0, 0))

        # Wave number
        wave_text = self.font.render(f"Wave: {self.wave_number} / {self.wave_manager.total_waves}", True, WHITE)
        self.screen.blit(wave_text, (20, 20))

        # Fast-forward button
        ff_button_rect = pygame.Rect(20, self.screen.get_height() - 70, 100, 50)
        pygame.draw.rect(self.screen, GREY, ff_button_rect, border_radius=5)
        ff_text = self.font.render(f"{self.game_speed}x", True, BLACK)
        self.screen.blit(ff_text, (ff_button_rect.centerx - ff_text.get_width() // 2, ff_button_rect.centery - ff_text.get_height() // 2))

        # Health bar
        health_bar_width = panel_width - 40
        # Settings button
        settings_button_rect = pygame.Rect(20, self.screen.get_height() - 140, 100, 50)
        pygame.draw.rect(self.screen, GREY, settings_button_rect, border_radius=5)
        settings_text = self.font.render("Settings", True, BLACK)
        self.screen.blit(settings_text, (settings_button_rect.centerx - settings_text.get_width() // 2, settings_button_rect.centery - settings_text.get_height() // 2))
        health_bar_height = 30
        health_pct = max(0, self.heartcrystal_health) / 100.0
        current_health_width = int(health_bar_width * health_pct)

        health_bar_rect = pygame.Rect(20, 70, health_bar_width, health_bar_height)
        current_health_rect = pygame.Rect(20, 70, current_health_width, health_bar_height)

        # Health bar gradient
        health_color = (int(255 * (1 - health_pct)), int(255 * health_pct), 0)

        pygame.draw.rect(self.screen, (50, 50, 50), health_bar_rect, border_radius=5)
        pygame.draw.rect(self.screen, health_color, current_health_rect, border_radius=5)
        
        health_text = self.font.render(f"{self.heartcrystal_health} / 100", True, WHITE)
        self.screen.blit(health_text, (health_bar_rect.centerx - health_text.get_width() // 2, health_bar_rect.centery - health_text.get_height() // 2))


    def draw_right_shop(self):
        panel_width = 300
        shop_panel = pygame.Surface((panel_width, self.screen.get_height()), pygame.SRCALPHA)
        shop_panel.fill((20, 20, 20, 180))
        self.screen.blit(shop_panel, (self.screen.get_width() - panel_width, 0))

        # --- Draw Selected Tower UI ---
        if self.selected_tower_instance:
            tower = self.selected_tower_instance
            
            # Tower Name
            name_text = self.font.render(f"{type(tower).__name__} (Lvl {tower.level})", True, WHITE)
            self.screen.blit(name_text, (self.screen.get_width() - panel_width + 20, 20))

            # Stats
            stats_y = 60
            stats = [
                f"Damage: {tower.damage}",
                f"Range: {tower.range}",
                f"Fire Rate: {tower.fire_rate / 1000.0:.2f}s"
            ]
            for i, stat in enumerate(stats):
                stat_text = self.font.render(stat, True, WHITE)
                self.screen.blit(stat_text, (self.screen.get_width() - panel_width + 20, stats_y + i * 30))

            # Upgrade Button
            upgrade_cost = tower.upgrade_cost
            can_afford_upgrade = self.meta_currency >= upgrade_cost
            upgrade_button_rect = pygame.Rect(self.screen.get_width() - panel_width + 20, stats_y + 100, panel_width - 40, 50)
            # Hover animation
            if upgrade_button_rect.collidepoint(pygame.mouse.get_pos()):
                pulse = (math.sin(pygame.time.get_ticks() * 0.01) + 1) / 2
                color = (int(GREEN[0] * (0.8 + 0.2 * pulse)), int(GREEN[1] * (0.8 + 0.2 * pulse)), int(GREEN[2] * (0.8 + 0.2 * pulse)))
            else:
                color = GREEN
            pygame.draw.rect(self.screen, color if can_afford_upgrade else GREY, upgrade_button_rect, border_radius=5)
            upgrade_text = self.font.render(f"Upgrade ({upgrade_cost})", True, BLACK)
            self.screen.blit(upgrade_text, (upgrade_button_rect.centerx - upgrade_text.get_width() // 2, upgrade_button_rect.centery - upgrade_text.get_height() // 2))

            # Sell Button
            sell_value = int(tower.cost * 0.65)
            sell_button_rect = pygame.Rect(self.screen.get_width() - panel_width + 20, stats_y + 160, panel_width - 40, 50)
            # Hover animation
            if sell_button_rect.collidepoint(pygame.mouse.get_pos()):
                pulse = (math.sin(pygame.time.get_ticks() * 0.01) + 1) / 2
                color = (int(RED[0] * (0.8 + 0.2 * pulse)), int(RED[1] * (0.8 + 0.2 * pulse)), int(RED[2] * (0.8 + 0.2 * pulse)))
            else:
                color = RED
            pygame.draw.rect(self.screen, color, sell_button_rect, border_radius=5)
            sell_text = self.font.render(f"Sell ({sell_value})", True, BLACK)
            self.screen.blit(sell_text, (sell_button_rect.centerx - sell_text.get_width() // 2, sell_button_rect.centery - sell_text.get_height() // 2))

        # --- Draw Shop UI ---
        else:
            # Currency display
            if self.perm_currency_fx_timer > 0: self.perm_currency_fx_timer -= 1
            if self.temp_currency_fx_timer > 0: self.temp_currency_fx_timer -= 1
            perm_color = self.perm_fx_color if self.perm_currency_fx_timer > 0 else WHITE
            temp_color = self.temp_fx_color if self.temp_currency_fx_timer > 0 else WHITE

            perm_currency_text = self.font.render(f"Aetherium: {self.meta_currency}", True, perm_color)
            temp_currency_text = self.font.render(f"Shards: {self.volatile_currency}", True, temp_color)
            
            self.screen.blit(perm_currency_text, (self.screen.get_width() - panel_width + 20, 20))
            self.screen.blit(temp_currency_text, (self.screen.get_width() - panel_width + 20, 60))

            # --- Draw Tower Cards ---
            start_y = 120
            card_height = 60
            for i, tower_data in enumerate(self.shop_towers):
                card_rect = pygame.Rect(self.screen.get_width() - panel_width + 10, start_y + i * card_height, panel_width - 20, card_height - 10)
                
                # Affordability
                can_afford = self.meta_currency >= tower_data["cost"] if tower_data["type"] != "barricade" else self.volatile_currency >= tower_data["cost"]
                border_color = (50, 50, 50) if not can_afford else (200, 200, 200)
                
                # Hover animation
                if card_rect.collidepoint(pygame.mouse.get_pos()):
                    pulse = (math.sin(pygame.time.get_ticks() * 0.01) + 1) / 2
                    bg_color = (int(40 + 20 * pulse), int(40 + 20 * pulse), int(40 + 20 * pulse))
                else:
                    bg_color = (40, 40, 40)
                
                pygame.draw.rect(self.screen, bg_color, card_rect, border_radius=5)
                pygame.draw.rect(self.screen, border_color, card_rect, 2, border_radius=5)

                icon_rect = pygame.Rect(card_rect.left + 5, card_rect.top + 5, 40, 40)
                pygame.draw.rect(self.screen, tower_data["color"], icon_rect, border_radius=5)

                name_text = self.font.render(tower_data["name"], True, WHITE)
                cost_text = self.font.render(str(tower_data["cost"]), True, WHITE if can_afford else RED)
                self.screen.blit(name_text, (card_rect.left + 55, card_rect.top + 5))
                self.screen.blit(cost_text, (card_rect.left + 55, card_rect.top + 30))

                # Tooltip
                if card_rect.collidepoint(pygame.mouse.get_pos()):
                    tooltip_text = f"Damage: {tower_data.get('damage', 'N/A')}, Range: {tower_data.get('range', 'N/A')}"
                    tooltip_surface = self.font.render(tooltip_text, True, BLACK)
                    tooltip_rect = tooltip_surface.get_rect(midbottom=card_rect.midtop)
                    pygame.draw.rect(self.screen, WHITE, tooltip_rect.inflate(10, 10))
                    self.screen.blit(tooltip_surface, tooltip_rect)

            # --- Draw Abilities ---
            overcharge_icon = pygame.Rect(self.screen.get_width() - panel_width + 20, self.screen.get_height() - 140, 50, 50)
            pygame.draw.rect(self.screen, YELLOW, overcharge_icon)
            overcharge_text = self.font.render(f"Overcharge", True, BLACK)
            self.screen.blit(overcharge_text, (self.screen.get_width() - panel_width + 80, self.screen.get_height() - 130))
            overcharge_cost_text = self.font.render(f"Cost: {OVERCHARGE_COST}", True, BLACK if self.volatile_currency >= OVERCHARGE_COST else RED)
            self.screen.blit(overcharge_cost_text, (self.screen.get_width() - panel_width + 80, self.screen.get_height() - 110))

            aoe_icon = pygame.Rect(self.screen.get_width() - panel_width + 20, self.screen.get_height() - 70, 50, 50)
            pygame.draw.rect(self.screen, RED, aoe_icon)
            aoe_text = self.font.render(f"AOE Attack", True, BLACK)
            self.screen.blit(aoe_text, (self.screen.get_width() - panel_width + 80, self.screen.get_height() - 60))
            aoe_cost_text = self.font.render(f"Cost: {AOE_ATTACK_COST}", True, BLACK if self.volatile_currency >= AOE_ATTACK_COST else RED)
            self.screen.blit(aoe_cost_text, (self.screen.get_width() - panel_width + 80, self.screen.get_height() - 40))

            # --- Tooltips for Abilities ---
            mouse_pos = pygame.mouse.get_pos()
            if overcharge_icon.collidepoint(mouse_pos):
                tooltip_lines = [
                    f"Overcharge",
                    f"Cost: {OVERCHARGE_COST} Shards",
                    f"Duration: {OVERCHARGE_DURATION / FPS}s",
                    f"Effect: +{int((OVERCHARGE_MULTIPLIER - 1) * 100)}% damage"
                ]
                self.draw_tooltip(tooltip_lines, overcharge_icon.midtop)

            if aoe_icon.collidepoint(mouse_pos):
                tooltip_lines = [
                    f"Aetheric Burst",
                    f"Cost: {AOE_ATTACK_COST} Shards",
                    f"Damage: {AOE_ATTACK_DAMAGE}",
                    f"Radius: {AOE_ATTACK_RADIUS}px"
                ]
                self.draw_tooltip(tooltip_lines, aoe_icon.midtop)

    def draw_placement_grid(self):
        if self.placing_plot:
            for spot in self.level.purchasable_tower_spots:
                is_occupied = any(p.rect.center == spot for p in self.spire_plots)
                if not is_occupied:
                    pygame.draw.circle(self.screen, (255, 255, 0, 100), spot, 25, 2)

    def draw_ghost_tower(self):
        mouse_pos = pygame.mouse.get_pos()
        
        if self.selected_tower:
            spire_color_map = { "sunfire": ORANGE, "frost": LIGHT_BLUE, "storm": PURPLE }
            base_color = spire_color_map.get(self.selected_tower, WHITE)
            
            is_valid_spot = False
            for plot in self.spire_plots:
                if not plot.is_occupied and plot.rect.collidepoint(mouse_pos):
                    is_valid_spot = True
                    break
            
            pulse = (math.sin(pygame.time.get_ticks() * 0.005) + 1) / 2
            alpha = 75 + (pulse * 100)
            ghost_image = pygame.Surface((50,50), pygame.SRCALPHA)
            ghost_image.fill((base_color[0], base_color[1], base_color[2], alpha))
            
            validity_color = GREEN if is_valid_spot else RED
            pygame.draw.circle(self.screen, validity_color, mouse_pos, 30, 2)
            self.screen.blit(ghost_image, (mouse_pos[0] - 25, mouse_pos[1] - 25))

        elif self.placing_barricade:
            is_valid_spot = False
            for spot in self.level.barricade_spots:
                if pygame.Rect(spot[0]-20, spot[1]-20, 40, 40).collidepoint(mouse_pos):
                    if not any(b.rect.center == spot for b in self.barricades):
                        is_valid_spot = True
                        break
            
            ghost_image = pygame.Surface((40,40), pygame.SRCALPHA)
            ghost_image.fill((BROWN[0], BROWN[1], BROWN[2], 150))
            validity_color = GREEN if is_valid_spot else RED
            pygame.draw.circle(self.screen, validity_color, mouse_pos, 25, 2)
            self.screen.blit(ghost_image, (mouse_pos[0] - 20, mouse_pos[1] - 20))

        elif self.placing_plot:
            is_valid_spot = False
            for spot in self.level.purchasable_tower_spots:
                if pygame.Rect(spot[0]-25, spot[1]-25, 50, 50).collidepoint(mouse_pos):
                    if not any(p.rect.center == spot for p in self.spire_plots):
                        is_valid_spot = True
                        break
            
            ghost_image = pygame.Surface((50,50), pygame.SRCALPHA)
            pygame.draw.circle(ghost_image, (0, 50, 0, 100), (25, 25), 25)
            validity_color = GREEN if is_valid_spot else RED
            pygame.draw.circle(self.screen, validity_color, mouse_pos, 30, 2)
            self.screen.blit(ghost_image, (mouse_pos[0] - 25, mouse_pos[1] - 25))

    def draw_ghost_aoe(self):
        mouse_pos = pygame.mouse.get_pos()
        overlay = pygame.Surface((AOE_ATTACK_RADIUS * 2, AOE_ATTACK_RADIUS * 2), pygame.SRCALPHA)
        pygame.draw.circle(overlay, (255, 0, 0, 100), (AOE_ATTACK_RADIUS, AOE_ATTACK_RADIUS), AOE_ATTACK_RADIUS)
        self.screen.blit(overlay, (mouse_pos[0] - AOE_ATTACK_RADIUS, mouse_pos[1] - AOE_ATTACK_RADIUS))

    def handle_mouse_click(self, pos):
        panel_width = 300
        icon_x = self.screen.get_width() - panel_width + 20
        
        # --- New Shop Click Handling ---
        panel_width = 300
        start_y = 120
        card_height = 60
        
        clicked_ui = False
        if self.selected_tower_instance:
            # Handle upgrade/sell clicks
            upgrade_button_rect = pygame.Rect(self.screen.get_width() - panel_width + 20, 160, panel_width - 40, 50)
            sell_button_rect = pygame.Rect(self.screen.get_width() - panel_width + 20, 220, panel_width - 40, 50)

            if upgrade_button_rect.collidepoint(pos):
                clicked_ui = True
                if self.meta_currency >= self.selected_tower_instance.upgrade_cost:
                    self.meta_currency -= self.selected_tower_instance.upgrade_cost
                    self.selected_tower_instance.upgrade()
                    if self.ui_click_sound: self.ui_click_sound.play()
            elif sell_button_rect.collidepoint(pos):
                clicked_ui = True
                self.meta_currency += int(self.selected_tower_instance.cost * 0.65)
                self.selected_tower_instance.kill()
                self.selected_tower_instance = None
                if self.ui_click_sound: self.ui_click_sound.play()

        else:
            for i, tower_data in enumerate(self.shop_towers):
                card_rect = pygame.Rect(self.screen.get_width() - panel_width + 10, start_y + i * card_height, panel_width - 20, card_height - 10)
                if card_rect.collidepoint(pos):
                    self.set_placing_state(tower_data["type"])
                    clicked_ui = True
                    break
        
        if clicked_ui and self.ui_click_sound:
            self.ui_click_sound.play()

        # --- Abilities ---
        overcharge_icon = pygame.Rect(self.screen.get_width() - panel_width + 20, self.screen.get_height() - 140, 50, 50)
        aoe_icon = pygame.Rect(self.screen.get_width() - panel_width + 20, self.screen.get_height() - 70, 50, 50)

        if overcharge_icon.collidepoint(pos):
            if self.volatile_currency >= OVERCHARGE_COST:
                self.volatile_currency -= OVERCHARGE_COST; self.temp_fx_color = ORANGE; self.temp_currency_fx_timer = 15
                self.overcharge_timer = OVERCHARGE_DURATION
                if self.ui_click_sound: self.ui_click_sound.play()
        elif aoe_icon.collidepoint(pos):
            if self.volatile_currency >= AOE_ATTACK_COST:
                self.set_placing_state("aoe")
                if self.ui_click_sound: self.ui_click_sound.play()
        
        # Map clicks
        elif not clicked_ui:
            # Check for fast-forward button click
            ff_button_rect = pygame.Rect(20, self.screen.get_height() - 70, 100, 50)
            if ff_button_rect.collidepoint(pos):
                if self.game_speed == 1:
                    self.game_speed = 2
                elif self.game_speed == 2:
                    self.game_speed = 4
                else:
                    self.game_speed = 1
                if self.ui_click_sound: self.ui_click_sound.play()
                return

            # Check for settings button click
            settings_button_rect = pygame.Rect(20, self.screen.get_height() - 140, 100, 50)
            if settings_button_rect.collidepoint(pos):
                self.game_state = "settings"
                if self.ui_click_sound: self.ui_click_sound.play()
                return

            # Adjust mouse position for camera offset
            map_width, map_height = self.level.width, self.level.height
            offset_x = (self.screen.get_width() - map_width) // 2
            offset_y = (self.screen.get_height() - map_height) // 2
            map_pos = (pos[0] - offset_x, pos[1] - offset_y)

            if self.placing_aoe_attack:
                if self.volatile_currency >= AOE_ATTACK_COST:
                    self.volatile_currency -= AOE_ATTACK_COST
                    self.temp_fx_color = ORANGE
                    self.temp_currency_fx_timer = 15
                    create_aoe_explosion(map_pos[0], map_pos[1], self.particles)
                    for enemy in list(self.enemies):
                        if math.hypot(map_pos[0] - enemy.rect.centerx, map_pos[1] - enemy.rect.centery) < AOE_ATTACK_RADIUS:
                            enemy.take_damage(AOE_ATTACK_DAMAGE, None)
                self.set_placing_state(None)
            elif self.selected_tower:
                for plot in self.spire_plots:
                    if not plot.is_occupied and plot.rect.collidepoint(map_pos):
                        if self.selected_tower == "sunfire" and self.meta_currency >= SUNFIRE_SPIRE_COST:
                            self.towers.add(SunfireSpire(plot.pos)); plot.is_occupied = True; self.meta_currency -= SUNFIRE_SPIRE_COST
                            self.perm_fx_color = ORANGE; self.perm_currency_fx_timer = 15
                        elif self.selected_tower == "frost" and self.meta_currency >= FROST_SPIRE_COST:
                            self.towers.add(FrostSpire(plot.pos)); plot.is_occupied = True; self.meta_currency -= FROST_SPIRE_COST
                            self.perm_fx_color = ORANGE; self.perm_currency_fx_timer = 15
                        elif self.selected_tower == "storm" and self.meta_currency >= STORM_SPIRE_COST:
                            self.towers.add(StormSpire(plot.pos)); plot.is_occupied = True; self.meta_currency -= STORM_SPIRE_COST
                            self.perm_fx_color = ORANGE; self.perm_currency_fx_timer = 15
                        self.set_placing_state(None)
                        break
            elif self.placing_barricade:
                for spot in self.level.barricade_spots:
                    if pygame.Rect(spot[0]-20, spot[1]-20, 40, 40).collidepoint(map_pos):
                        if not any(b.rect.center == spot for b in self.barricades) and self.volatile_currency >= BARRICADE_COST:
                            self.barricades.add(Barricade(spot)); self.volatile_currency -= BARRICADE_COST
                            self.temp_fx_color = ORANGE; self.temp_currency_fx_timer = 15
                        self.set_placing_state(None)
                        break
            elif self.placing_plot:
                for spot in self.level.purchasable_tower_spots:
                    if pygame.Rect(spot[0]-25, spot[1]-25, 50, 50).collidepoint(map_pos):
                        if not any(p.rect.center == spot for p in self.spire_plots) and self.meta_currency >= SPIRE_PLOT_COST:
                            self.spire_plots.add(SpirePlot(spot)); self.meta_currency -= SPIRE_PLOT_COST
                            self.perm_fx_color = ORANGE; self.perm_currency_fx_timer = 15
                        self.set_placing_state(None)
                        break
            else: # No placement mode, check for selecting a tower
                for tower in self.towers:
                    if tower.rect.collidepoint(map_pos):
                        self.selected_tower_instance = tower
                        self.set_placing_state(None) # Exit any placing mode
                        return # Exit after selecting
                # If no tower was clicked, deselect
                self.selected_tower_instance = None

    def handle_enemy_deaths(self):
        for enemy in list(self.enemies):
            if enemy.health <= 0:
                self.volatile_currency += 50
                self.temp_fx_color = GREEN
                self.temp_currency_fx_timer = 15
                create_dissolve_effect(enemy.rect.centerx, enemy.rect.centery, self.particles)
                if enemy.death_sound:
                    enemy.death_sound.play()
                enemy.kill()

    def handle_enemy_abilities(self):
        for enemy in self.enemies:
            if isinstance(enemy, ChronoWarper) and enemy.can_pulse():
                enemy.reset_pulse_timer()
                for tower in self.towers:
                    dist = math.hypot(enemy.rect.centerx - tower.rect.centerx, enemy.rect.centery - tower.rect.centery)
                    if dist < CHRONO_WARPER_PULSE_RADIUS:
                        tower.slow_effect_timer = CHRONO_WARPER_SLOW_DURATION

    def draw_enemy_abilities(self):
        for enemy in self.enemies:
            if isinstance(enemy, ChronoWarper) and enemy.pulse_vfx_timer > 0:
                progress = 1 - (enemy.pulse_vfx_timer / (FPS / 2))
                radius = int(CHRONO_WARPER_PULSE_RADIUS * progress)
                alpha = int(255 * (1 - progress))
                
                overlay = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(overlay, (255, 0, 255, alpha), (radius, radius), radius, 3)
                self.screen.blit(overlay, (enemy.rect.centerx - radius, enemy.rect.centery - radius))

    def handle_wave_spawning(self):
        if not self.enemies and self.wave_timer <= 0:
            if self.wave_number > 0:
                converted_amount = int(self.volatile_currency * VOLATILE_TO_META_CONVERSION_RATIO)
                self.meta_currency += converted_amount
                self.volatile_currency = 0
                self.perm_fx_color = GREEN
                self.perm_currency_fx_timer = 15
            
            self.wave_number += 1
            self.wave_timer = 10 * FPS
            self.wave_took_damage = False
            new_enemies = self.wave_manager.get_wave(self.wave_number)
            for enemy in new_enemies:
                self.enemies.add(enemy)
        elif not self.enemies:
            self.wave_timer -= 1

    def check_collisions(self):
        for enemy in list(self.enemies):
            if enemy.path_index >= len(enemy.path) - 1:
                self.heartcrystal_health -= 10
                self.wave_took_damage = True
                enemy.kill()

    def draw_game_over(self):
        self.screen.fill(BLACK)
        game_over_text = self.font.render("Game Over", True, WHITE)
        restart_text = self.font.render("Press 'R' to return to Main Menu", True, WHITE)
        self.screen.blit(game_over_text, (self.screen.get_width() // 2 - game_over_text.get_width() // 2, self.screen.get_height() // 2 - 50))
        self.screen.blit(restart_text, (self.screen.get_width() // 2 - restart_text.get_width() // 2, self.screen.get_height() // 2 + 50))

    def draw_win_screen(self):
        self.screen.fill(BLACK)
        win_text = self.font.render("You Win!", True, WHITE)
        restart_text = self.font.render("Press 'R' to return to Main Menu", True, WHITE)
        self.screen.blit(win_text, (self.screen.get_width() // 2 - win_text.get_width() // 2, self.screen.get_height() // 2 - 50))
        self.screen.blit(restart_text, (self.screen.get_width() // 2 - restart_text.get_width() // 2, self.screen.get_height() // 2 + 50))

    def check_win_loss(self):
        if self.heartcrystal_health <= 0:
            self.save_progress()
            self.game_state = "game_over"
        
        if self.wave_number >= 10 and not self.enemies:
            self.save_progress()
            self.game_state = "win"

    def reset_run(self, level_data):
        self.level = Level(level_data["map_data"])
        self.wave_manager = WaveManager(self.level.path)
        # pygame.mixer.music.load(assets.MUSIC_LEVEL_1)
        # pygame.mixer.music.play(-1)
        self.heartcrystal_health = 100
        self.volatile_currency = level_data["starting_volatile_currency"]
        self.wave_number = 0
        self.wave_timer = 5 * FPS
        self.enemies.empty()
        self.towers.empty()
        self.projectiles.empty()
        self.particles.empty()
        self.barricades.empty()
        self.setup_level()
        self.set_placing_state(None)
        self.overcharge_timer = 0
        self.game_state = "playing"

    def setup_level(self):
        self.spire_plots.empty()
        for spot in self.level.initial_tower_spots:
            self.spire_plots.add(SpirePlot(spot))

    def set_placing_state(self, state):
        self.selected_tower = state if state in ["sunfire", "frost", "storm"] else None
        self.placing_barricade = state == "barricade"
        self.placing_aoe_attack = state == "aoe"
        self.placing_plot = state == "plot"

    def draw_tooltip(self, lines, pos):
        font = pygame.font.Font(None, 24)
        padding = 5
        
        # Find max width
        max_width = 0
        for line in lines:
            text_surface = font.render(line, True, BLACK)
            if text_surface.get_width() > max_width:
                max_width = text_surface.get_width()

        total_height = len(lines) * (font.get_height() + 2)
        
        tooltip_surface = pygame.Surface((max_width + padding * 2, total_height + padding * 2))
        tooltip_surface.fill(WHITE)
        
        for i, line in enumerate(lines):
            text_surface = font.render(line, True, BLACK)
            tooltip_surface.blit(text_surface, (padding, padding + i * (font.get_height() + 2)))
            
        tooltip_rect = tooltip_surface.get_rect(midbottom=pos)
        self.screen.blit(tooltip_surface, tooltip_rect)

    def draw_main_menu(self):
        # self.screen.blit(self.bg_main_menu, (0,0))
        self.screen.fill(BLACK) # Placeholder
        title_text = self.title_font.render("Aetheria: The Last Stand", True, WHITE)
        currency_text = self.font.render(f"Aetherium: {self.meta_currency}", True, WHITE)
        start_text = self.font.render("Press SPACE to Select Level", True, WHITE)
        
        self.screen.blit(title_text, (self.screen.get_width() // 2 - title_text.get_width() // 2, self.screen.get_height() // 2 - 150))
        self.screen.blit(currency_text, (self.screen.get_width() // 2 - currency_text.get_width() // 2, self.screen.get_height() // 2 - 50))
        self.screen.blit(start_text, (self.screen.get_width() // 2 - start_text.get_width() // 2, self.screen.get_height() // 2 + 50))

        # Armory Button (Placeholder)
        armory_button = pygame.Rect(self.screen.get_width() // 2 - 150, self.screen.get_height() // 2 + 120, 300, 50)
        pygame.draw.rect(self.screen, GREY, armory_button)
        armory_text = self.font.render("Armory (Coming Soon)", True, BLACK)
        self.screen.blit(armory_text, (armory_button.centerx - armory_text.get_width() // 2, armory_button.centery - armory_text.get_height() // 2))

    def draw_level_select_menu(self):
        self.screen.fill(BLACK)
        title_text = self.title_font.render("Select a Level", True, WHITE)
        self.screen.blit(title_text, (self.screen.get_width() // 2 - title_text.get_width() // 2, 100))

        for i, level_data in enumerate(levels.ALL_LEVELS):
            level_button = pygame.Rect(self.screen.get_width() // 2 - 150, 250 + i * 70, 300, 50)
            pygame.draw.rect(self.screen, GREY, level_button)
            level_text = self.font.render(f"{level_data['name']} ({level_data['difficulty']})", True, BLACK)
            self.screen.blit(level_text, (level_button.centerx - level_text.get_width() // 2, level_button.centery - level_text.get_height() // 2))

    def save_progress(self):
        try:
            with open("savegame.json", "r") as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {"unlocks": []} # Start fresh if file is bad
        
        data["meta_currency"] = self.meta_currency
        
        with open("savegame.json", "w") as f:
            json.dump(data, f, indent=4)

    def load_progress(self):
        try:
            with open("savegame.json", "r") as f:
                data = json.load(f)
                self.meta_currency = data.get("meta_currency", 500)
        except (FileNotFoundError, json.JSONDecodeError):
            self.meta_currency = 500 # Default value if no save exists

    def load_assets(self):
        # self.bg_main_menu = pygame.image.load(assets.BG_MAIN_MENU).convert()
        # self.bg_level_1 = pygame.image.load(assets.BG_LEVEL_1).convert()
        # self.castle_image = pygame.image.load(assets.CASTLE_IMAGE).convert_alpha()
        self.castle_image = assets.get_placeholder_surface(80, 80, (200, 200, 200)) # Placeholder

        # self.ui_click_sound = pygame.mixer.Sound(assets.SFX_UI_CLICK)
        self.ui_click_sound = None

    def toggle_pause(self):
        self.is_paused = not self.is_paused

    def draw_pause_menu(self):
        overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0,0))
        
        pause_text = self.title_font.render("Paused", True, WHITE)
        self.screen.blit(pause_text, (self.screen.get_width() // 2 - pause_text.get_width() // 2, self.screen.get_height() // 2 - 50))

    def draw_settings_menu(self):
        self.screen.fill(BLACK)
        title_text = self.title_font.render("Settings", True, WHITE)
        self.screen.blit(title_text, (self.screen.get_width() // 2 - title_text.get_width() // 2, 100))

        # Music Volume
        music_text = self.font.render(f"Music Volume: {int(self.music_volume * 100)}%", True, WHITE)
        self.screen.blit(music_text, (self.screen.get_width() // 2 - 150, 250))
        music_up_button = pygame.Rect(self.screen.get_width() // 2 + 100, 250, 30, 30)
        music_down_button = pygame.Rect(self.screen.get_width() // 2 + 50, 250, 30, 30)
        pygame.draw.rect(self.screen, GREY, music_up_button)
        pygame.draw.rect(self.screen, GREY, music_down_button)

        # SFX Volume
        sfx_text = self.font.render(f"SFX Volume: {int(self.sfx_volume * 100)}%", True, WHITE)
        self.screen.blit(sfx_text, (self.screen.get_width() // 2 - 150, 300))
        sfx_up_button = pygame.Rect(self.screen.get_width() // 2 + 100, 300, 30, 30)
        sfx_down_button = pygame.Rect(self.screen.get_width() // 2 + 50, 300, 30, 30)
        pygame.draw.rect(self.screen, GREY, sfx_up_button)
        pygame.draw.rect(self.screen, GREY, sfx_down_button)

        # Back Button
        back_button = pygame.Rect(self.screen.get_width() // 2 - 100, 400, 200, 50)
        pygame.draw.rect(self.screen, GREY, back_button)
        back_text = self.font.render("Back", True, BLACK)
        self.screen.blit(back_text, (back_button.centerx - back_text.get_width() // 2, back_button.centery - back_text.get_height() // 2))

        # Level Select Button
        level_select_button = pygame.Rect(self.screen.get_width() // 2 - 100, 470, 200, 50)
        pygame.draw.rect(self.screen, GREY, level_select_button)
        level_select_text = self.font.render("Level Select", True, BLACK)
        self.screen.blit(level_select_text, (level_select_button.centerx - level_select_text.get_width() // 2, level_select_button.centery - level_select_text.get_height() // 2))

    def handle_level_select_click(self, pos):
        for i, level_data in enumerate(levels.ALL_LEVELS):
            level_button = pygame.Rect(self.screen.get_width() // 2 - 150, 250 + i * 70, 300, 50)
            if level_button.collidepoint(pos):
                self.reset_run(level_data)
                break

    def handle_settings_click(self, pos):
        # Music Volume
        music_up_button = pygame.Rect(self.screen.get_width() // 2 + 100, 250, 30, 30)
        music_down_button = pygame.Rect(self.screen.get_width() // 2 + 50, 250, 30, 30)
        if music_up_button.collidepoint(pos):
            self.music_volume = min(1.0, self.music_volume + 0.1)
        elif music_down_button.collidepoint(pos):
            self.music_volume = max(0.0, self.music_volume - 0.1)

        # SFX Volume
        sfx_up_button = pygame.Rect(self.screen.get_width() // 2 + 100, 300, 30, 30)
        sfx_down_button = pygame.Rect(self.screen.get_width() // 2 + 50, 300, 30, 30)
        if sfx_up_button.collidepoint(pos):
            self.sfx_volume = min(1.0, self.sfx_volume + 0.1)
        elif sfx_down_button.collidepoint(pos):
            self.sfx_volume = max(0.0, self.sfx_volume - 0.1)

        # Back Button
        back_button = pygame.Rect(self.screen.get_width() // 2 - 100, 400, 200, 50)
        if back_button.collidepoint(pos):
            self.game_state = "playing"

        # Level Select Button
        level_select_button = pygame.Rect(self.screen.get_width() // 2 - 100, 470, 200, 50)
        if level_select_button.collidepoint(pos):
            self.game_state = "level_select"

if __name__ == "__main__":
    game = Game()
    game.run()