import pygame
import sys
import math
import json
from settings import *
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
        self.font = pygame.font.Font(None, 36)
        
        # --- CURRENCY & PROGRESSION REFACTOR ---
        self.permanent_currency = 500 # Start with a fixed amount
        self.temporary_currency = 0
        # self.load_progress() # TEMP: Disabled for single-level build

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
        self.placing_barricade = False
        self.placing_plot = False
        self.placing_aoe_attack = False
        self.overcharge_timer = 0
        self.game_state = "main_menu" # Start in the main menu
        self.setup_level()
        self.wave_took_damage = False

        # UI Feedback timers
        self.perm_currency_fx_timer = 0
        self.temp_currency_fx_timer = 0
        self.perm_fx_color = WHITE
        self.temp_fx_color = WHITE

    def run(self):
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
                elif self.game_state in ["game_over", "win"]:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r:
                            self.game_state = "main_menu"
                elif self.game_state == "main_menu":
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            self.reset_run()

            if self.game_state == "playing":
                self.update()
                self.draw()
            elif self.game_state == "game_over":
                self.draw_game_over()
            elif self.game_state == "win":
                self.draw_win_screen()
            elif self.game_state == "main_menu":
                self.draw_main_menu()

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

    def update(self):
        if self.game_state != "playing":
            return
        
        if self.overcharge_timer > 0:
            self.overcharge_timer -= 1
        damage_multiplier = OVERCHARGE_MULTIPLIER if self.overcharge_timer > 0 else 1.0
        
        self.enemies.update(self.particles, self.barricades)
        self.towers.update(self.enemies, self.projectiles, self.particles, self.screen, damage_multiplier)
        self.particles.update()
        
        self.handle_wave_spawning()
        self.check_collisions()
        self.handle_enemy_deaths()
        self.handle_enemy_abilities()
        self.check_win_loss()

    def draw(self):
        self.screen.fill(BLACK)
        self.level.draw(self.screen)
        self.spire_plots.draw(self.screen)
        self.enemies.draw(self.screen)
        self.towers.draw(self.screen)
        self.barricades.draw(self.screen)
        self.particles.draw(self.screen)
        
        for tower in self.towers:
            tower.draw_vfx(self.screen)

        self.draw_hud()
        self.draw_tower_ui()
        
        if self.selected_tower or self.placing_barricade or self.placing_plot:
            self.draw_placement_grid()
            self.draw_ghost_tower()
        elif self.placing_aoe_attack:
            self.draw_ghost_aoe()
            
        self.draw_enemy_abilities()

    def draw_hud(self):
        if self.perm_currency_fx_timer > 0: self.perm_currency_fx_timer -= 1
        if self.temp_currency_fx_timer > 0: self.temp_currency_fx_timer -= 1

        perm_color = self.perm_fx_color if self.perm_currency_fx_timer > 0 else WHITE
        temp_color = self.temp_fx_color if self.temp_currency_fx_timer > 0 else WHITE

        health_text = self.font.render(f"Heartcrystal: {self.heartcrystal_health}", True, WHITE)
        perm_currency_text = self.font.render(f"Permanent Currency: {self.permanent_currency}", True, perm_color)
        temp_currency_text = self.font.render(f"Temporary Currency: {self.temporary_currency}", True, temp_color)
        wave_text = self.font.render(f"Wave: {self.wave_number}", True, WHITE)
        self.screen.blit(health_text, (10, 10))
        self.screen.blit(perm_currency_text, (10, 50))
        self.screen.blit(temp_currency_text, (10, 90))
        self.screen.blit(wave_text, (10, 130))

    def draw_tower_ui(self):
        panel_width = 300
        ui_panel = pygame.Rect(self.screen.get_width() - panel_width, 0, panel_width, self.screen.get_height())
        pygame.draw.rect(self.screen, GREY, ui_panel)

        icon_x = self.screen.get_width() - panel_width + 20
        text_x = self.screen.get_width() - panel_width + 80

        # Affordability Colors
        can_afford_sunfire = self.permanent_currency >= SUNFIRE_SPIRE_COST
        can_afford_frost = self.permanent_currency >= FROST_SPIRE_COST
        can_afford_storm = self.permanent_currency >= STORM_SPIRE_COST
        can_afford_plot = self.permanent_currency >= SPIRE_PLOT_COST
        can_afford_barricade = self.temporary_currency >= BARRICADE_COST
        can_afford_overcharge = self.temporary_currency >= OVERCHARGE_COST
        can_afford_aoe = self.temporary_currency >= AOE_ATTACK_COST

        sunfire_color = WHITE if can_afford_sunfire else RED
        frost_color = WHITE if can_afford_frost else RED
        storm_color = WHITE if can_afford_storm else RED
        plot_color = WHITE if can_afford_plot else RED
        barricade_color = WHITE if can_afford_barricade else RED
        overcharge_color = BLACK if can_afford_overcharge else RED
        aoe_color = WHITE if can_afford_aoe else RED

        sunfire_icon = pygame.Rect(icon_x, 50, 50, 50)
        pygame.draw.rect(self.screen, ORANGE, sunfire_icon)
        sunfire_text = self.font.render(f"Sunfire Spire: {SUNFIRE_SPIRE_COST}", True, sunfire_color)
        self.screen.blit(sunfire_text, (text_x, 65))

        frost_icon = pygame.Rect(icon_x, 120, 50, 50)
        pygame.draw.rect(self.screen, LIGHT_BLUE, frost_icon)
        frost_text = self.font.render(f"Frost Spire: {FROST_SPIRE_COST}", True, frost_color)
        self.screen.blit(frost_text, (text_x, 135))

        storm_icon = pygame.Rect(icon_x, 190, 50, 50)
        pygame.draw.rect(self.screen, PURPLE, storm_icon)
        storm_text = self.font.render(f"Storm Spire: {STORM_SPIRE_COST}", True, storm_color)
        self.screen.blit(storm_text, (text_x, 205))

        barricade_icon = pygame.Rect(icon_x, 260, 50, 50)
        pygame.draw.rect(self.screen, BROWN, barricade_icon)
        barricade_text = self.font.render(f"Barricade: {BARRICADE_COST}", True, barricade_color)
        self.screen.blit(barricade_text, (text_x, 275))

        overcharge_icon = pygame.Rect(icon_x, 330, 50, 50)
        pygame.draw.rect(self.screen, YELLOW, overcharge_icon)
        overcharge_text = self.font.render(f"Overcharge: {OVERCHARGE_COST}", True, overcharge_color)
        self.screen.blit(overcharge_text, (text_x, 345))

        aoe_icon = pygame.Rect(icon_x, 400, 50, 50)
        pygame.draw.rect(self.screen, RED, aoe_icon)
        aoe_text = self.font.render(f"AOE Attack: {AOE_ATTACK_COST}", True, aoe_color)
        self.screen.blit(aoe_text, (text_x, 415))
        
        plot_icon = pygame.Rect(icon_x, 470, 50, 50)
        pygame.draw.rect(self.screen, DARK_BLUE, plot_icon)
        plot_text = self.font.render(f"Spire Plot: {SPIRE_PLOT_COST}", True, plot_color)
        self.screen.blit(plot_text, (text_x, 485))

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
        
        sunfire_icon = pygame.Rect(icon_x, 50, 50, 50)
        frost_icon = pygame.Rect(icon_x, 120, 50, 50)
        storm_icon = pygame.Rect(icon_x, 190, 50, 50)
        barricade_icon = pygame.Rect(icon_x, 260, 50, 50)
        overcharge_icon = pygame.Rect(icon_x, 330, 50, 50)
        aoe_icon = pygame.Rect(icon_x, 400, 50, 50)
        plot_icon = pygame.Rect(icon_x, 470, 50, 50)

        # UI clicks
        if sunfire_icon.collidepoint(pos): self.set_placing_state("sunfire")
        elif frost_icon.collidepoint(pos): self.set_placing_state("frost")
        elif storm_icon.collidepoint(pos): self.set_placing_state("storm")
        elif barricade_icon.collidepoint(pos): self.set_placing_state("barricade")
        elif plot_icon.collidepoint(pos): self.set_placing_state("plot")
        elif overcharge_icon.collidepoint(pos):
            if self.temporary_currency >= OVERCHARGE_COST:
                self.temporary_currency -= OVERCHARGE_COST
                self.temp_fx_color = ORANGE
                self.temp_currency_fx_timer = 15
                self.overcharge_timer = OVERCHARGE_DURATION
        elif aoe_icon.collidepoint(pos):
            if self.temporary_currency >= AOE_ATTACK_COST:
                self.set_placing_state("aoe")
        
        # Map clicks
        else:
            if self.placing_aoe_attack:
                if self.temporary_currency >= AOE_ATTACK_COST:
                    self.temporary_currency -= AOE_ATTACK_COST
                    self.temp_fx_color = ORANGE
                    self.temp_currency_fx_timer = 15
                    create_aoe_explosion(pos[0], pos[1], self.particles)
                    for enemy in list(self.enemies):
                        if math.hypot(pos[0] - enemy.rect.centerx, pos[1] - enemy.rect.centery) < AOE_ATTACK_RADIUS:
                            enemy.take_damage(AOE_ATTACK_DAMAGE, None)
                self.set_placing_state(None)
            elif self.selected_tower:
                for plot in self.spire_plots:
                    if not plot.is_occupied and plot.rect.collidepoint(pos):
                        if self.selected_tower == "sunfire" and self.permanent_currency >= SUNFIRE_SPIRE_COST:
                            self.towers.add(SunfireSpire(plot.pos)); plot.is_occupied = True; self.permanent_currency -= SUNFIRE_SPIRE_COST
                            self.perm_fx_color = ORANGE; self.perm_currency_fx_timer = 15
                        elif self.selected_tower == "frost" and self.permanent_currency >= FROST_SPIRE_COST:
                            self.towers.add(FrostSpire(plot.pos)); plot.is_occupied = True; self.permanent_currency -= FROST_SPIRE_COST
                            self.perm_fx_color = ORANGE; self.perm_currency_fx_timer = 15
                        elif self.selected_tower == "storm" and self.permanent_currency >= STORM_SPIRE_COST:
                            self.towers.add(StormSpire(plot.pos)); plot.is_occupied = True; self.permanent_currency -= STORM_SPIRE_COST
                            self.perm_fx_color = ORANGE; self.perm_currency_fx_timer = 15
                        self.set_placing_state(None)
                        break
            elif self.placing_barricade:
                for spot in self.level.barricade_spots:
                    if pygame.Rect(spot[0]-20, spot[1]-20, 40, 40).collidepoint(pos):
                        if not any(b.rect.center == spot for b in self.barricades) and self.temporary_currency >= BARRICADE_COST:
                            self.barricades.add(Barricade(spot)); self.temporary_currency -= BARRICADE_COST
                            self.temp_fx_color = ORANGE; self.temp_currency_fx_timer = 15
                        self.set_placing_state(None)
                        break
            elif self.placing_plot:
                for spot in self.level.purchasable_tower_spots:
                    if pygame.Rect(spot[0]-25, spot[1]-25, 50, 50).collidepoint(pos):
                        if not any(p.rect.center == spot for p in self.spire_plots) and self.permanent_currency >= SPIRE_PLOT_COST:
                            self.spire_plots.add(SpirePlot(spot)); self.permanent_currency -= SPIRE_PLOT_COST
                            self.perm_fx_color = ORANGE; self.perm_currency_fx_timer = 15
                        self.set_placing_state(None)
                        break

    def handle_enemy_deaths(self):
        for enemy in list(self.enemies):
            if enemy.health <= 0:
                self.temporary_currency += 50
                self.temp_fx_color = GREEN
                self.temp_currency_fx_timer = 15
                create_dissolve_effect(enemy.rect.centerx, enemy.rect.centery, self.particles)
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
                conversion_rate = 1.1 if not self.wave_took_damage else 0.9
                converted_amount = int(self.temporary_currency * conversion_rate)
                self.permanent_currency += converted_amount
                self.temporary_currency = 0
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
            # self.save_progress() # TEMP: Disabled
            self.game_state = "game_over"
        
        if self.wave_number >= 10 and not self.enemies:
            # self.save_progress() # TEMP: Disabled
            self.game_state = "win"

    def reset_run(self):
        self.heartcrystal_health = 100
        self.temporary_currency = 0
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

    def draw_main_menu(self):
        self.screen.fill(BLACK)
        title_text = self.font.render("Aetheria: The Last Stand", True, WHITE)
        currency_text = self.font.render(f"Aetherium: {self.permanent_currency}", True, WHITE)
        start_text = self.font.render("Press SPACE to Start", True, WHITE)
        
        self.screen.blit(title_text, (self.screen.get_width() // 2 - title_text.get_width() // 2, self.screen.get_height() // 2 - 100))
        self.screen.blit(currency_text, (self.screen.get_width() // 2 - currency_text.get_width() // 2, self.screen.get_height() // 2))
        self.screen.blit(start_text, (self.screen.get_width() // 2 - start_text.get_width() // 2, self.screen.get_height() // 2 + 100))

    def save_progress(self):
        # TEMP: Disabled for single-level build
        pass

    def load_progress(self):
        # TEMP: Disabled for single-level build
        self.permanent_currency = 500

if __name__ == "__main__":
    game = Game()
    game.run()