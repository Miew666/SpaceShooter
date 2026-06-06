"""Aufsammelbare Power-Ups — Laser-Stufe oder Drohnen-Begleiter."""

import pygame

import settings
from assets import Assets


class PowerUpType:
    """Typen von Power-Ups."""

    LASER = "laser"
    DRONE = "drone"


class PowerUp(pygame.sprite.Sprite):
    """Fällt von zerstörten Gegnern und bewegt sich langsam nach unten."""

    def __init__(self, x: int, y: int, powerup_type: str = PowerUpType.LASER):
        super().__init__()
        self.powerup_type = powerup_type
        if powerup_type == PowerUpType.DRONE:
            self.image = Assets.powerup_drone.copy()
        else:
            self.image = Assets.powerup_laser.copy()
        self.rect = self.image.get_rect(center=(x, y))

    def update(self) -> None:
        """Langsam nach unten fallen; außerhalb des Bildschirms entfernen."""
        self.rect.y += settings.POWERUP_SPEED
        if self.rect.top > settings.SCREEN_HEIGHT:
            self.kill()
