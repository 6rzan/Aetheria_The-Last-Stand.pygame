# Changelog

This document tracks the major architectural changes and feature implementations for the Aetheria tower defense game.

## [Initial] - Core Gameplay & Asset Scaffolding

### Added
- **Initial Game Structure:**
  - Created the main game loop in `main.py` with basic state management (main menu, playing, game over).
  - Implemented core classes for `Tower`, `Enemy`, and `Level` in their respective files.
- **Asset Management System:**
  - Established `assets.py` to centralize all file paths, improving maintainability.
  - Implemented placeholder surfaces for all visual assets to ensure the game was runnable without final art.

## [Phase 1] - UI/UX and Gameplay Overhaul

This was a massive update that transformed the game from a basic prototype into a feature-rich experience with a modern UI and deeper gameplay mechanics.

### Added
- **Complete UI/UX Redesign:**
  - **Three-Panel Layout:** Implemented a new UI with a left-side HUD, a right-side dynamic shop/info panel, and a centered game map.
  - **Centered Map & Camera:** The game world is now rendered in the center of the screen, with a camera offset applied to all game objects.
  - **Dynamic HUD:** The left HUD displays wave info and a gradient-colored health bar.
- **Tower Progression:**
  - Implemented tower upgrading and selling functionality.
- **New Content:**
  - Added the "Healer" enemy archetype.
  - Created three distinct level maps with different path layouts.
- **Game Flow Controls:**
  - Implemented Pause, Fast-Forward, and a Settings menu with volume controls.
  - Added a Level Selection screen.
- **UI Polish:**
  - Added detailed tooltips and hover animations to shop items and abilities.

### Fixed
- **Numerous Crashes:** Resolved critical `AttributeError` crashes related to incorrect class scope, missing attributes in the `WaveManager`, and invalid color values for the health bar.
- **VFX Rendering:** Corrected major bugs where all visual effects were not rendering correctly due to the new camera system.

## [Phase 2] - Economic Overhaul & Dynamic Difficulty

This update focused on refining the core gameplay loop with a more strategic economy and difficulty scaling.

### Added
- **Dual-Currency Economy:**
  - **Volatile Currency (Shards):** Earned from kills, spent on in-run tactical actions.
  - **Permanent Currency (Aetherium):** Converted from Shards at the end of a wave, used for meta-progression.
- **Dynamic Difficulty:**
  - Levels now have "Easy," "Normal," and "Hard" difficulties, which scale the amount of starting Volatile Currency.
- **Meta-Progression Framework:**
  - Implemented a save/load system for Permanent Currency using a `savegame.json` file.
  - Added a placeholder "Armory" button to the main menu for future features.

### Changed
- **Economic Flow:** Refactored all in-game costs to use the new dual-currency system.

## [Phase 3] - Visual Polish and Scaling Overhaul

This update addressed extensive user feedback on visual consistency, asset integration, and the overall scale of the game world.

### Added
- **Full Asset Integration:**
  - Replaced all placeholder graphics with the user-provided image assets for towers, enemies, plots, castles, and backgrounds.
- **Responsive Backgrounds:**
  - The main menu and in-game backgrounds now dynamically scale to fit the window size.
- **Enemy Spawn Gate:**
  - The `Heartcrystal_Castle.png` is now used as a decorative spawn gate at the start of the enemy path.

### Changed
- **Game World Scaling:**
  - Significantly increased the size of all core gameplay elements (towers, enemies, plots, path) for better visibility and a more cohesive look.
  - Manually re-adjusted all hardcoded level coordinates to fit the new, larger scale.
- **Path Rendering:**
  - Reworked the path drawing logic to render a textured path using `Path_Tile.png` on top of a colored base, restoring the "old map shape" as requested.
- **Asset Roles:**
  - Corrected the usage of castle assets. `castle.png` is now the main target base, and `Heartcrystal_Castle.png` is the enemy spawn point.

### Fixed
- **Spire Plot Reusability:** Fixed a critical bug preventing players from building on a plot after selling a tower.
- **Placement Previews:** Resolved a major bug where placement previews used incorrect coordinates, making placement impossible on some levels.
- **Asset Scaling:** Corrected the scale of all tower and plot images to fit their designated areas.

## [Version 1.1] - Gameplay Depth and Strategic Diversity

This update significantly expands the strategic options available to the player by introducing new tactical abilities, enemy types with unique mechanics, and a more dynamic in-game economy.

### Added
- **New Enemy Archetypes:**
  - **Chrono Warper:** A disruptive enemy that emits a temporal pulse, slowing the attack speed of all nearby towers.
  - **Saboteur:** Upon death, this enemy disables the tower that delivered the final blow for a short duration.
- **New Player Abilities (Volatile Currency):**
  - **Barricades:** Place temporary, high-health obstacles on the path to stall enemies.
  - **Aetheric Burst:** A powerful, player-activated AOE damage ability.
  - **Overcharge:** Temporarily doubles the damage of all towers.
- **New Tower Mechanics:**
  - **Sunfire Spire:** Now locks onto a single target until it's destroyed or moves out of range.
  - **Storm Spire:** Now attacks all enemies within its range simultaneously with chain lightning VFX.
- **New Structures:**
  - **Spire Plots:** Players can now purchase and place new tower plots on designated map locations using permanent currency.
- **Enhanced UI & Feedback:**
  - Added detailed tooltips for all abilities in the shop, showing cost, duration, and effects.
  - Implemented visual feedback for currency gains and expenditures.
  - Added visual effects for the Chrono Warper's pulse and the Healer's pulse.

### Changed
- **Tower Targeting:**
  - Frost Spire no longer deals damage and exclusively applies a slowing effect.
- **Economy:**
  - Rebalanced costs for all towers, abilities, and plots to fit the new dual-currency system.
- **Settings:**
  - The settings menu is now accessible from the main menu and in-game.
  - Added a "Level Select" button to the settings menu for easier navigation.

### Fixed
- **Save/Load:** Corrected an issue where the game would not load the correct amount of meta currency.
- **UI:** Fixed various minor UI bugs related to button alignment and text rendering.

## [Phase 4] - Documentation

### Added
- **Release Notes:** Created `release_notes.md` to provide players with a comprehensive overview of the game's features, progress, and recent changes.
