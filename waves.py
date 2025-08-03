import random
from enemies import ShadowCrawler, ShadowFlyer, ShieldingSentinel, ChronoWarper, Saboteur

class WaveManager:
    def __init__(self, path):
        self.path = path

    def get_wave(self, wave_number):
        wave_enemies = []
        
        # Simple scaling for basic enemies
        num_crawlers = wave_number * 3
        num_flyers = wave_number * 2

        for _ in range(num_crawlers):
            wave_enemies.append(ShadowCrawler(self.path))
        for _ in range(num_flyers):
            wave_enemies.append(ShadowFlyer(self.path))

        # Introduce new archetypes
        if wave_number >= 4:
            num_sentinels = (wave_number - 3) * 1
            for _ in range(num_sentinels):
                wave_enemies.append(ShieldingSentinel(self.path))

        if wave_number >= 6:
            num_warpers = (wave_number - 5) * 1
            for _ in range(num_warpers):
                wave_enemies.append(ChronoWarper(self.path))

        if wave_number >= 8:
            num_saboteurs = (wave_number - 7) * 1
            for _ in range(num_saboteurs):
                wave_enemies.append(Saboteur(self.path))

        # Future: Add synergistic squads here

        random.shuffle(wave_enemies)
        return wave_enemies