"""Sternenhintergrund — zufällige Punkte auf schwarzem Hintergrund."""

import random

import pygame

import settings


class Starfield:
    """Zeichnet statische Sterne als einfache Punkte."""

    def __init__(self):
        # Liste von (x, y, helligkeit) — beim Start einmal erzeugen
        self._stars = [
            (
                random.randint(0, settings.SCREEN_WIDTH - 1),
                random.randint(0, settings.SCREEN_HEIGHT - 1),
                random.choice([settings.COLOR_WHITE, settings.COLOR_GRAY]),
            )
            for _ in range(settings.STAR_COUNT)
        ]

    def draw(self, surface: pygame.Surface) -> None:
        """Sterne auf die Oberfläche zeichnen (vor den Sprites aufrufen)."""
        for x, y, color in self._stars:
            surface.set_at((x, y), color)
