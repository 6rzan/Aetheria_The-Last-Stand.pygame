# Changelog

## [YYYY-MM-DD] - Asset Management & UI Scaffolding

### Added
- **Asset Management System:**
  - Created `assets.py` to centralize all file paths for game assets (images, sounds, music, fonts).
  - Organized asset paths into a logical directory structure (`assets/images/`, `assets/sounds/`, etc.).
  - This provides a single source of truth for asset loading and will make managing assets much easier in the future.

### Changed
- **Game Logic Integration:**
  - Updated the main game logic (`main.py`, `towers.py`, `enemies.py`, etc.) to import asset paths from `assets.py`.
  - All asset loading code (e.g., `pygame.image.load()`) has been commented out.
  - **Placeholder Assets:** To ensure the game remains fully runnable, temporary visual placeholders (e.g., colored `pygame.Surface` objects) have been implemented for all visual assets. This allows for development and testing to continue without the final art assets.
  - Sound loading has been disabled and guarded with checks to prevent crashes.

## [YYYY-MM-DD] - Gameplay Systems and UI Overhaul

This update represents a complete overhaul of the user interface and a massive expansion of core gameplay systems, moving the project from a basic prototype to a feature-rich game.

### Added
- **Complete UI/UX Overhaul:**
  - **New Layout:** The entire UI was redesigned with a three-panel layout: a left-side HUD for game status, a right-side Shop/Info panel, and a centered game map.
  - **Centered Map:** The game world is now rendered in the center of the screen, with a camera offset applied to all game objects for correct positioning.
  - **Dynamic HUD:** The left HUD displays the current wave, total waves, and a dynamic, gradient-colored health bar for the Heartcrystal.
  - **Interactive Shop:** The right panel serves as a shop for towers and abilities, and dynamically switches to an info panel when a placed tower is selected.
- **Tower Progression System:**
  - **Upgrading:** Players can now select placed towers and spend `meta_currency` to upgrade them, increasing their stats.
  - **Selling:** Placed towers can be sold for 65% of their total invested cost.
- **New Enemy Archetype:**
  - **Healer:** A new support enemy that periodically heals other nearby enemies.
- **Game Flow and Controls:**
  - **Pause Menu:** Players can now pause the game by pressing 'P'.
  - **Fast-Forward:** A button on the HUD allows players to cycle through 1x, 2x, and 4x game speeds.
  - **Settings Menu:** A settings menu is now accessible from the HUD, allowing control over music and SFX volume. It also provides options to return to the game or the level select screen.
  - **Level Selection:** A dedicated level select screen allows players to choose from multiple maps.
- **UI Polish:**
  - **Tooltips:** Detailed tooltips now appear when hovering over tower cards and abilities in the shop, showing stats and costs.
  - **Hover Animations:** UI buttons and tower cards now feature subtle animations on mouse-over for better feedback.

### Changed
- **Core Gameplay Loop:** The game flow now moves from a main menu to a level select screen, and then into the core game.
- **Level Structure:** The `levels.py` data structure was updated to support multiple, distinct maps.
- **Enemy AI:** The base `Enemy.update` method was modified to accept a list of all enemies, enabling the Healer's area-of-effect abilities.

### Fixed
- **Critical `AttributeError`:** Resolved a persistent crash caused by multiple game-flow methods being defined outside the main `Game` class scope in `main.py`.
- **`WaveManager` Crash:** Fixed a crash caused by a missing `total_waves` attribute.
- **VFX Rendering:** Corrected a major bug where tower attack VFX were not being rendered correctly due to the new camera offset system. All VFX are now properly aligned with the game world.
- **Color Value Crash:** Fixed a `ValueError` that occurred when the Heartcrystal's health dropped below zero, causing an invalid color to be calculated for the health bar.
- **Enemy Color Reset:** Fixed an `AttributeError` that occurred when a slowed enemy's effect wore off, caused by a missing `original_color` attribute.

## [YYYY-MM-DD] - Economic Overhaul & Dynamic Difficulty

This update refines the core gameplay loop by implementing a strategic dual-currency economy and a dynamic difficulty framework.

### Added
- **Dual-Currency Economy:**
  - **Volatile Currency (Shards):** Earned from enemy kills during a wave. Used for tactical, in-run actions like activating abilities and buying barricades. Resets at the start of a new level.
  - **Permanent Currency (Aetherium):** Earned by converting unspent Shards at the end of a wave. Used for strategic, meta-progression purchases like towers and upgrades.
- **Dynamic Difficulty:**
  - The level data in `levels.py` now includes a difficulty setting ("Easy", "Normal", "Hard").
  - The amount of starting Volatile Currency is now scaled based on the chosen level's difficulty, providing a variable challenge.
- **Meta-Progression Framework:**
  - **Data Persistence:** The player's Permanent Currency is now saved to and loaded from a `savegame.json` file, creating persistence between game sessions.
  - **UI Placeholder:** A disabled "Armory" button has been added to the main menu to serve as a placeholder for future meta-progression features.

### Changed
- **Economic Flow:** The entire in-game economy was refactored to use the new dual-currency system. Tower and plot costs were mapped to Permanent Currency, while tactical abilities were mapped to Volatile Currency.
- **End-of-Wave Cycle:** The end-of-wave bonus logic was simplified to a flat conversion ratio of Volatile to Permanent currency, defined in `settings.py`.
