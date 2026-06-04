"""Spieler-Projektil."""

import pygame

import settings


class Bullet(pygame.sprite.Sprite):
    """Projektil, das nach oben fliegt und Gegner zerstört."""

    def __init__(self, x: int, y: int):
        super().__init__()
        self.image = self._create_image()
        self.rect = self.image.get_rect(center=(x, y))

    def _create_image(self) -> pygame.Surface:
        """Grafik erzeugen — später durch pygame.image.load(...) ersetzen."""
        surface = pygame.Surface(
            (settings.BULLET_WIDTH, settings.BULLET_HEIGHT), pygame.SRCALPHA
        )
        pygame.draw.rect(
            surface,
            settings.COLOR_BULLET,
            (0, 0, settings.BULLET_WIDTH, settings.BULLET_HEIGHT),
            border_radius=2,
        )
        return surface

    def update(self) -> None:
        """Projektil nach oben bewegen; außerhalb des Bildschirms entfernen."""
        self.rect.y -= settings.BULLET_SPEED
        if self.rect.bottom < 0:
            self.kill()
