import pygame
import sys
import math
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, BLACK, WHITE, GREY, ORANGE, LIGHT_BLUE, PURPLE, RED, GREEN, SUNFIRE_SPIRE_COST, FROST_SPIRE_COST, STORM_SPIRE_COST
from levels import Level, LEVEL_1_MAP, LEVEL_2_MAP
from towers import SunfireSpire, FrostSpire, StormSpire
from enemies import ShadowCrawler, ShadowFlyer
from effects import create_explosion, create_dissolve_effect

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Aetheria: The Last Stand")
        self.clock = pygame.time.Clock()
        self.level = Level(LEVEL_1_MAP)
        self.font = pygame.font.Font(None, 36)
        self.heartcrystal_health = 100
        self.currency = 500
        self.wave_number = 0
        self.wave_timer = 5 * FPS
        self.enemies = pygame.sprite.Group()
        self.towers = pygame.sprite.Group()
        self.projectiles = pygame.sprite.Group()
        self.particles = pygame.sprite.Group()
        self.selected_tower = None
        self.game_state = "playing" # playing, game_over, win

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if self.game_state == "playing":
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1: # Left-click
                            self.handle_mouse_click(event.pos)
                        elif event.button == 3: # Right-click
                            if self.selected_tower:
                                self.selected_tower = None # Cancel selection
                elif self.game_state in ["game_over", "win"]:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r:
                            self.__init__() # Restart the game

            if self.game_state == "playing":
                self.update()
                self.draw()
            elif self.game_state == "game_over":
                self.draw_game_over()
            elif self.game_state == "win":
                self.draw_win_screen()


            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

    def update(self):
        if self.game_state != "playing":
            return
        
        # Update all game objects
        self.enemies.update(self.particles)
        self.towers.update(self.enemies, self.projectiles, self.particles, self.screen)
        self.particles.update()
        
        # Handle game logic
        self.handle_wave_spawning()
        self.check_collisions()
        self.check_win_loss()

    def draw(self):
        self.screen.fill(BLACK)
        self.level.draw(self.screen)
        self.enemies.draw(self.screen)
        self.towers.draw(self.screen)
        self.particles.draw(self.screen)
        
        # Draw tower VFX
        for tower in self.towers:
            tower.draw_vfx(self.screen)

        self.draw_hud()
        self.draw_tower_ui()
        if self.selected_tower:
            self.draw_placement_grid()
            self.draw_ghost_tower()

    def draw_hud(self):
        health_text = self.font.render(f"Heartcrystal: {self.heartcrystal_health}", True, WHITE)
        currency_text = self.font.render(f"Currency: {self.currency}", True, WHITE)
        wave_text = self.font.render(f"Wave: {self.wave_number}", True, WHITE)
        self.screen.blit(health_text, (10, 10))
        self.screen.blit(currency_text, (10, 50))
        self.screen.blit(wave_text, (10, 90))

    def draw_tower_ui(self):
        # Enhanced UI for selecting towers
        ui_panel = pygame.Rect(SCREEN_WIDTH - 220, 0, 220, SCREEN_HEIGHT)
        pygame.draw.rect(self.screen, GREY, ui_panel)

        # Sunfire Spire
        sunfire_icon = pygame.Rect(SCREEN_WIDTH - 200, 50, 50, 50)
        pygame.draw.rect(self.screen, ORANGE, sunfire_icon)
        sunfire_text = self.font.render(f"Sunfire: {SUNFIRE_SPIRE_COST}", True, WHITE)
        self.screen.blit(sunfire_text, (SCREEN_WIDTH - 140, 65))

        # Frost Spire
        frost_icon = pygame.Rect(SCREEN_WIDTH - 200, 120, 50, 50)
        pygame.draw.rect(self.screen, LIGHT_BLUE, frost_icon)
        frost_text = self.font.render(f"Frost: {FROST_SPIRE_COST}", True, WHITE)
        self.screen.blit(frost_text, (SCREEN_WIDTH - 140, 135))

        # Storm Spire
        storm_icon = pygame.Rect(SCREEN_WIDTH - 200, 190, 50, 50)
        pygame.draw.rect(self.screen, PURPLE, storm_icon)
        storm_text = self.font.render(f"Storm: {STORM_SPIRE_COST}", True, WHITE)
        self.screen.blit(storm_text, (SCREEN_WIDTH - 140, 205))

    def draw_placement_grid(self):
        for spot in self.level.tower_spots:
            is_occupied = any(tower.rect.center == spot for tower in self.towers)
            if is_occupied:
                pygame.draw.circle(self.screen, (255, 0, 0, 100), spot, 25, 3)
            else:
                pygame.draw.circle(self.screen, (0, 255, 0, 100), spot, 25, 3)

    def draw_ghost_tower(self):
        if self.selected_tower:
            mouse_pos = pygame.mouse.get_pos()
            
            # 1. Determine Spire Color
            spire_color_map = {
                "sunfire": ORANGE,
                "frost": LIGHT_BLUE,
                "storm": PURPLE
            }
            base_color = spire_color_map.get(self.selected_tower, WHITE)

            # 2. Determine Placement Validity
            is_valid_spot = False
            for spot in self.level.tower_spots:
                 if pygame.Rect(spot[0]-25, spot[1]-25, 50, 50).collidepoint(mouse_pos):
                    if not any(tower.rect.center == spot for tower in self.towers):
                        is_valid_spot = True
                        break
            
            # 3. Create Pulsing Ghost Image
            pulse = (math.sin(pygame.time.get_ticks() * 0.005) + 1) / 2 # 0 to 1 sine wave
            alpha = 75 + (pulse * 100) # Pulsing alpha between 75 and 175
            
            ghost_image = pygame.Surface((50,50), pygame.SRCALPHA)
            ghost_image.fill((base_color[0], base_color[1], base_color[2], alpha))
            
            # 4. Draw Validity Circle and Ghost Image
            validity_color = GREEN if is_valid_spot else RED
            pygame.draw.circle(self.screen, validity_color, mouse_pos, 30, 2)
            self.screen.blit(ghost_image, (mouse_pos[0] - 25, mouse_pos[1] - 25))

    def handle_mouse_click(self, pos):
        # Tower selection UI
        sunfire_icon = pygame.Rect(SCREEN_WIDTH - 200, 50, 50, 50)
        frost_icon = pygame.Rect(SCREEN_WIDTH - 200, 120, 50, 50)
        storm_icon = pygame.Rect(SCREEN_WIDTH - 200, 190, 50, 50)
        if sunfire_icon.collidepoint(pos):
            self.selected_tower = "sunfire"
        elif frost_icon.collidepoint(pos):
            self.selected_tower = "frost"
        elif storm_icon.collidepoint(pos):
            self.selected_tower = "storm"
        else:
            # Tower placement
            if self.selected_tower:
                for spot in self.level.tower_spots:
                    if pygame.Rect(spot[0]-25, spot[1]-25, 50, 50).collidepoint(pos):
                        is_occupied = any(tower.rect.center == spot for tower in self.towers)
                        if not is_occupied:
                            if self.selected_tower == "sunfire" and self.currency >= SUNFIRE_SPIRE_COST:
                                self.towers.add(SunfireSpire(spot))
                                self.currency -= SUNFIRE_SPIRE_COST
                            elif self.selected_tower == "frost" and self.currency >= FROST_SPIRE_COST:
                                self.towers.add(FrostSpire(spot))
                                self.currency -= FROST_SPIRE_COST
                            elif self.selected_tower == "storm" and self.currency >= STORM_SPIRE_COST:
                                self.towers.add(StormSpire(spot))
                                self.currency -= STORM_SPIRE_COST
                        self.selected_tower = None
                        break # Exit after placing a tower

    def handle_wave_spawning(self):
        if not self.enemies and self.wave_timer <= 0:
            self.wave_number += 1
            self.wave_timer = 5 * FPS
            for i in range(self.wave_number * 5): # Simple scaling
                enemy_type = ShadowCrawler if i % 2 == 0 else ShadowFlyer
                self.enemies.add(enemy_type(self.level.path))
        elif not self.enemies:
            self.wave_timer -=1


    def check_collisions(self):
        # Enemy reaching the end
        for enemy in list(self.enemies): # Iterate over a copy
            if enemy.path_index >= len(enemy.path) - 1:
                self.heartcrystal_health -= 10
                enemy.kill()


    def draw_game_over(self):
        self.screen.fill(BLACK)
        game_over_text = self.font.render("Game Over", True, WHITE)
        restart_text = self.font.render("Press 'R' to Restart", True, WHITE)
        self.screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))

    def draw_win_screen(self):
        self.screen.fill(BLACK)
        win_text = self.font.render("You Win!", True, WHITE)
        restart_text = self.font.render("Press 'R' to Restart", True, WHITE)
        self.screen.blit(win_text, (SCREEN_WIDTH // 2 - win_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))

    def check_win_loss(self):
        if self.heartcrystal_health <= 0:
            self.game_state = "game_over"
        
        if self.wave_number >= 10 and not self.enemies: # Win after 10 waves
            self.game_state = "win"

if __name__ == "__main__":
    game = Game()
    game.run()