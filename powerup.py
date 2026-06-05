"""Aufsammelbares Power-Up — erhöht die Laser-Stufe des Spielers."""

import pygame

import settings
from assets import Assets


class PowerUp(pygame.sprite.Sprite):
    """Fällt von zerstörten Gegnern und bewegt sich langsam nach unten."""

    def __init__(self, x: int, y: int):
        super().__init__()
        self.image = Assets.powerup_laser.copy()
        self.rect = self.image.get_rect(center=(x, y))

    def update(self) -> None:
        """Langsam nach unten fallen; außerhalb des Bildschirms entfernen."""
        self.rect.y += settings.POWERUP_SPEED
        if self.rect.top > settings.SCREEN_HEIGHT:
            self.kill()
