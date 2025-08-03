# Changelog

This document tracks the major architectural changes and feature implementations for the tower defense game.

## Project Refactoring and Stability Overhaul

The project underwent a significant refactoring to address core stability issues and improve the overall architecture. The previous incremental fixes were insufficient, leading to a full architectural review and rebuild of key systems.

### 1. Main Game Loop Refactoring
- **File:** `main.py`
- **Change:** The main game loop was restructured to safely handle game object updates, attacks, and visual effects (VFX). This prevents crashes related to objects being destroyed while being accessed.
- **Outcome:** A more resilient and stable game loop.

### 2. Tower Logic Simplification
- **File:** `towers.py`
- **Change:** The base `Tower` class was simplified to focus solely on target acquisition. All specialized attack logic was moved into the respective tower subclasses (`SunfireSpire`, `FrostSpire`, `StormSpire`).
- **Outcome:** Clearer separation of concerns and easier maintenance of individual tower behaviors.

### 3. Sunfire Spire Rebuild
- **Files:** `towers.py`, `effects.py`
- **Changes:**
    - Attack logic was clarified to deal direct damage to a single target.
    - A new `create_explosion` particle effect was implemented for visual feedback.
    - A beam VFX was added that correctly displays for a short duration after an attack.
- **Outcome:** A stable, single-target damage tower with clear and functional VFX.

### 4. Frost Spire Rebuild
- **Files:** `towers.py`, `effects.py`, `enemies.py`
- **Changes:**
    - The attack now correctly deals damage in addition to applying a slow effect.
    - A new `create_frost_effect` was added for particle VFX upon impact.
    - The slow mechanism was verified, and enemies now visually change color to indicate they are slowed.
- **Outcome:** A functional crowd-control tower that deals damage and reliably slows enemies.

### 5. Storm Spire Rebuild
- **Files:** `towers.py`, `effects.py`
- **Changes:**
    - The Area of Effect (AOE) damage is now correctly centered on the primary target, not the tower.
    - A new `create_storm_effect` was implemented to replace the generic explosion effect.
    - The AOE visual indicator is now correctly drawn at the target's location with a color that matches the tower's theme.
- **Outcome:** A working AOE damage tower with accurate and thematic visual effects.

### 6. Final Stability Test
- **Action:** Executed the game (`py main.py`).
- **Result:** The game runs without any crashes. Enemies are spawned, targeted, and defeated correctly by all tower types. The core gameplay is stable.

## Post-Refactor Adjustments

Based on user feedback, several adjustments were made to align tower behavior and visuals with the intended design.

### 1. Game Loop Draw Order Correction
- **Files:** `main.py`, `towers.py`
- **Change:** Corrected a fundamental flaw in the game loop where VFX were drawn during the `update` phase, causing them to be immediately erased by the `draw` phase's screen clear. The `draw_vfx` call was moved from `Tower.update` to `Game.draw`, ensuring effects are rendered in the correct order.
- **Outcome:** All tower visual effects (beams, AOE circles) are now correctly and reliably rendered to the screen. This was the root cause of the "invisible VFX" issue.

### 1. Tower VFX Visibility
- **File:** `towers.py`
- **Change:** Removed the `.alive()` check from the `draw_vfx` method for all towers. This ensures that visual effects (like the Sunfire Spire's beam) are rendered for their full duration, even if the target is destroyed in the same frame as the attack.
- **Outcome:** Tower attack visuals are now consistently and reliably displayed.

### 2. Frost Spire Damage Removal
- **File:** `towers.py`
- **Change:** Removed the line of code that caused the Frost Spire to deal damage.
- **Outcome:** The Frost Spire now functions purely as a crowd-control tower, slowing enemies without dealing damage, as originally intended.

### 3. Storm Spire VFX Enhancement
- **File:** `towers.py`
- **Change:** The `draw_vfx` method for the Storm Spire was enhanced. It now draws a more prominent AOE circle (with a border and stronger fill color) and a beam from the tower to the primary target.
- **Outcome:** The AOE attack is now much clearer visually, indicating both the primary target and the area of effect.

## VFX and Gameplay Polish Pass

Further user feedback prompted a final polish pass on tower visual effects and gameplay mechanics.

### 1. Frost Spire VFX Overhaul
- **File:** `towers.py`
- **Change:** The Frost Spire's beam VFX was replaced with a "frozen area" effect. It now draws a semi-transparent circle of ice on the ground under the slowed target, providing a distinct and thematic visual indicator for its effect.
- **Outcome:** The Frost Spire now has a unique visual identity that clearly communicates its function.

### 2. Storm Spire AOE and VFX Update
- **Files:** `settings.py`, `towers.py`
- **Changes:**
    - The AOE radius was increased from 50 to 80 to make its damage more effective and noticeable.
    - The VFX was completely overhauled to be a "pulsing" shockwave. The confusing beam was removed, and the AOE circle now grows and fades, creating a dynamic visual that better represents an area attack.
- **Outcome:** The Storm Spire is now a more effective AOE tower with a clear, satisfying visual effect that matches its function.

### 3. Storm Spire Targeting Fix
- **File:** `settings.py`
- **Change:** Increased the `STORM_SPIRE_RANGE` from 100 to 140. The tower's previous short range was preventing it from acquiring targets in many common placements, making it appear non-functional.
- **Outcome:** The Storm Spire now reliably acquires targets and fires, resolving the final issue with its functionality.

### 4. Storm Spire Final Tuning
- **Files:** `settings.py`, `effects.py`, `towers.py`
- **Change:** Based on final feedback, the Storm Spire was tuned to be less overwhelming. Damage was lowered, the AOE radius was reduced to a more balanced size, the particle count was decreased, and the pulse animation was slowed down.
- **Outcome:** The Storm Spire is now a balanced and visually pleasing AOE tower.

### 5. Final Polish and VFX Overhaul
- **Files:** `settings.py`, `effects.py`, `towers.py`
- **Changes:**
    - Weakened the damage of both the Sunfire Spire and Storm Spire for better game balance.
    - Completely overhauled the Storm Spire's visual effect to be a "chain lightning" attack. The pulsing circle was removed in favor of jagged lines of lightning that connect the primary target to all other enemies hit in the AOE.
    - The storm particle effect was changed to be more like sparks to match the new lightning theme.
- **Outcome:** The game is now balanced according to feedback, and the Storm Spire has a unique, thematic, and visually exciting attack.

### 6. Final Damage Balancing
- **File:** `settings.py`
- **Change:** Performed one last damage reduction on the Sunfire Spire (20 -> 15) and Storm Spire (8 -> 6) to finalize game balance. (Update: Further reduced to Sunfire: 12, Storm: 5).
- **Outcome:** Tower damage values are now finalized.

### 7. Sunfire Spire Target Locking
- **File:** `towers.py`
- **Change:** Implemented a target-locking mechanism for the Sunfire Spire. It now overrides the default `update` method to lock onto a single target and will continue to attack it until it is defeated or moves out of range.
- **Outcome:** The Sunfire Spire now behaves as a dedicated single-target eliminator, as requested.

### 8. Storm Spire Final AOE Tuning
- **File:** `settings.py`
- **Change:** After confirming the AOE mechanic was working, the Storm Spire's damage and radius were tuned to a final, balanced state (Damage: 10, Radius: 90) to ensure the effect was noticeable without being overpowered.
- **Outcome:** The Storm Spire's AOE attack is now functionally correct and balanced for gameplay.

## Quality of Life Features

### 1. Placement Cancellation
- **File:** `main.py`
- **Change:** Implemented a right-click cancellation feature. While holding a tower for placement, the user can now right-click to cancel the action, returning them to a neutral state without placing the tower.
- **Outcome:** Improved user experience by providing an intuitive way to back out of a placement decision.

### 2. Enhanced Placement Preview
- **File:** `main.py`
- **Change:** Overhauled the "ghost tower" preview. Instead of a simple red/green square, it now shows a pulsing, semi-transparent image of the selected tower in its correct color. Placement validity is now indicated by a colored circle drawn underneath the preview.
- **Outcome:** Provides a much more intuitive and visually appealing placement experience.

### 3. Crash Fix for Placement Preview
- **Files:** `main.py`, `settings.py`
- **Change:** Fixed a `NameError` crash that occurred when selecting a tower. The `RED` color constant was missing from `settings.py` and the wildcard import in `main.py` was replaced with an explicit import list to prevent similar issues.
- **Outcome:** The game is now stable and no longer crashes upon selecting a tower.

## Dynamic Difficulty and Rewards System

This major feature overhaul introduces a comprehensive system for dynamic difficulty scaling and strategic player rewards, creating a more engaging and challenging gameplay loop.

### 1. New Enemy Archetypes
- **File:** `enemies.py`, `settings.py`, `towers.py`
- **Change:** Introduced three new enemy archetypes with unique abilities:
    - **Shielding Sentinel:** Blocks a fixed amount of damage with a regenerating shield.
    - **Chrono-Warper:** Periodically emits a pulse that slows the attack speed of nearby towers.
    - **Saboteur:** Disables the tower that delivers the killing blow for a short duration.
- **Outcome:** Increased strategic depth and enemy variety.

### 2. Dynamic Wave Generation
- **Files:** `waves.py`, `main.py`
- **Change:** Replaced the simple wave spawning logic with a `WaveManager` class. This new system dynamically generates waves with an escalating number and variety of enemies, introducing the new archetypes at predefined wave milestones.
- **Outcome:** A more structured and progressively challenging wave experience.

### 3. Dual-Currency Economy
- **File:** `main.py`, `enemies.py`
- **Change:** Implemented a dual-currency system:
    - **Shards (Temporary):** Earned by defeating enemies, used for in-run tactical abilities.
    - **Aetherium (Permanent):** Awarded for surviving waves, intended for future meta-progression.
- **Outcome:** Creates a framework for both immediate tactical decisions and long-term player progression.

### 4. Barricade System
- **Files:** `structures.py`, `levels.py`, `main.py`, `enemies.py`
- **Change:** Added a deployable barricade system. Players can spend temporary currency to place barricades on predefined hardpoints. Enemies will now stop and attack barricades that block their path.
- **Outcome:** Introduces a new layer of strategic map control and enemy pathing manipulation.

### 5. In-Run Tactical Abilities
- **Files:** `main.py`, `settings.py`, `effects.py`, `towers.py`
- **Change:** Added two powerful, single-use abilities purchasable with temporary currency:
    - **Weapon Overcharge:** Temporarily doubles the damage of all towers.
    - **AOE Attack:** Allows the player to trigger a large, high-damage explosion anywhere on the map.
- **Outcome:** Provides players with reactive tools to handle difficult situations.

### 6. Meta-Progression Framework
- **File:** `main.py`
- **Change:** Implemented the foundational framework for meta-progression. The game now features a main menu, and permanent currency is saved to a `savegame.json` file between runs.
- **Outcome:** Creates a persistent gameplay loop where players can accumulate currency for future unlocks.

## Gameplay and UI Refactoring

This pass focused on implementing new core gameplay mechanics and improving the user experience based on detailed requirements.

### 1. Purchasable Spire Plots
- **Files:** `main.py`, `levels.py`, `structures.py`, `settings.py`
- **Change:** Overhauled the tower placement system. Players no longer have fixed spots but start with a few initial "Spire Plots." They can now purchase additional plots from the shop using permanent currency and place them on predefined strategic locations, expanding their defensive options.
- **Outcome:** Adds a new strategic layer to the game, making map control and resource management more critical.

### 2. UI Enhancements
- **Files:** `main.py`, `structures.py`
- **Changes:**
    - **Enlarged Shop:** The shop UI panel was widened to prevent text from being cut off, ensuring all item names and costs are clearly legible.
    - **Barricade Visibility:** The barricade sprite was updated with a high-contrast yellow border to make it easily distinguishable from the game path.
- **Outcome:** Improved UI clarity and a better user experience.

### 3. Critical Crash Fix
- **File:** `enemies.py`
- **Change:** Resolved a `TypeError` that occurred when the game updated enemies. The `update` methods for the new enemy archetypes had inconsistent arguments compared to the base `Enemy` class. The method signatures were synchronized to fix the crash.
- **Outcome:** The game is now stable and runs without crashing when new enemy types are present.

### 4. Controls and Resizing
- **File:** `main.py`
- **Changes:**
    - **Resizable Window:** The game window is now fully resizable. UI elements in the shop panel are now positioned relative to the screen size.
    - **Purchasing Bug Fix:** Corrected a bug where the clickable areas for the UI buttons did not match their visual location after the shop panel was resized, making it impossible to purchase multiple items.
- **Outcome:** A more flexible display and corrected control scheme.

## Economy Refactor and UI Polish

This pass completely overhauls the in-game economy to focus on a single-level, wave-based loop and adds dynamic UI feedback.

### 1. System Isolation
- **File:** `main.py`
- **Change:** The meta-progression save/load system has been temporarily commented out to support a single-level gameplay experience. The game now starts with a fixed amount of permanent currency and the main menu has been restored.
- **Outcome:** The game is now a self-contained, single-run experience with a clear starting point.

### 2. Two-Tier Currency System
- **File:** `main.py`
- **Change:** The economy was refactored into two distinct types:
    - **Permanent Currency:** Persists between waves, used for major purchases like towers and plots.
    - **Temporary Currency:** Earned from kills within a wave and spent on tactical abilities.
- **Outcome:** Creates a more engaging economic loop with both strategic and tactical spending decisions.

### 3. End-of-Wave Economic Cycle
- **File:** `main.py`
- **Change:** At the end of each wave, all remaining temporary currency is converted into permanent currency. A bonus is awarded for not taking damage, and a penalty is applied if damage was taken. The temporary currency is then reset to zero.
- **Outcome:** Rewards skillful play and provides a clear economic cycle for each wave.

### 4. Dynamic Currency UI
- **File:** `main.py`
- **Changes:**
    - **Gain/Loss Feedback:** The currency display in the HUD now briefly flashes green for gains and orange for spends.
    - **Affordability Indicator:** The price text for items in the shop now turns red if the player cannot afford them, providing clear, immediate feedback.
- **Outcome:** A more responsive and intuitive user interface.
