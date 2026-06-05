"""Gegner-Projektil — bewegt sich nach unten und unterscheidet sich optisch vom Spieler-Schuss."""

import pygame

import settings


class EnemyLaser(pygame.sprite.Sprite):
    """Laser/Projektil eines Gegners, das nach unten fliegt."""

    def __init__(self, x: int, y: int):
        super().__init__()
        self.image = self._create_image()
        self.rect = self.image.get_rect(midtop=(x, y))

    def _create_image(self) -> pygame.Surface:
        """Grafik erzeugen — später durch pygame.image.load(...) ersetzen."""
        surface = pygame.Surface(
            (settings.ENEMY_LASER_WIDTH, settings.ENEMY_LASER_HEIGHT), pygame.SRCALPHA
        )
        pygame.draw.rect(
            surface,
            settings.COLOR_ENEMY_LASER,
            (0, 0, settings.ENEMY_LASER_WIDTH, settings.ENEMY_LASER_HEIGHT),
            border_radius=2,
        )
        return surface

    def update(self) -> None:
        """Projektil nach unten bewegen; außerhalb des Bildschirms entfernen."""
        self.rect.y += settings.ENEMY_LASER_SPEED
        if self.rect.top > settings.SCREEN_HEIGHT:
            self.kill()
