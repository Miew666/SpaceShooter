"""Gegnerisches Raumschiff."""

import random

import pygame

import settings


class Enemy(pygame.sprite.Sprite):
    """Gegner, der von oben nach unten driftet und oben respawnt."""

    def __init__(self, x: int, y: int):
        super().__init__()
        self.image = self._create_image()
        self.rect = self.image.get_rect(topleft=(x, y))

    def _create_image(self) -> pygame.Surface:
        """Grafik erzeugen — später durch pygame.image.load(...) ersetzen."""
        surface = pygame.Surface(
            (settings.ENEMY_WIDTH, settings.ENEMY_HEIGHT), pygame.SRCALPHA
        )
        # Invertiertes Dreieck (Spitze nach unten)
        points = [
            (settings.ENEMY_WIDTH // 2, settings.ENEMY_HEIGHT),
            (0, 0),
            (settings.ENEMY_WIDTH, 0),
        ]
        pygame.draw.polygon(surface, settings.COLOR_ENEMY, points)
        pygame.draw.polygon(surface, settings.COLOR_ENEMY_ACCENT, points, 2)
        return surface

    @classmethod
    def spawn_at_top(cls) -> "Enemy":
        """Neuen Gegner am oberen Bildschirmrand mit zufälliger X-Position erzeugen."""
        x = random.randint(0, settings.SCREEN_WIDTH - settings.ENEMY_WIDTH)
        return cls(x, -settings.ENEMY_HEIGHT)

    def update(self) -> None:
        """Gegner nach unten bewegen; am unteren Rand oben neu spawnen."""
        self.rect.y += settings.ENEMY_SPEED
        if self.rect.top > settings.SCREEN_HEIGHT:
            self.rect.bottom = 0
            self.rect.x = random.randint(
                0, settings.SCREEN_WIDTH - settings.ENEMY_WIDTH
            )
