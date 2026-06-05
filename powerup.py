"""Aufsammelbares Power-Up — erhöht die Laser-Stufe des Spielers."""

import pygame

import settings


class PowerUp(pygame.sprite.Sprite):
    """Fällt von zerstörten Gegnern und bewegt sich langsam nach unten."""

    def __init__(self, x: int, y: int):
        super().__init__()
        self.image = self._create_image()
        self.rect = self.image.get_rect(center=(x, y))

    def _create_image(self) -> pygame.Surface:
        """Grafik erzeugen — später durch pygame.image.load(...) ersetzen."""
        size = settings.POWERUP_SIZE
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        # Leuchtendes grünes Power-Up-Symbol
        pygame.draw.circle(surface, settings.COLOR_POWERUP, (size // 2, size // 2), size // 2 - 2)
        pygame.draw.circle(surface, settings.COLOR_POWERUP_GLOW, (size // 2, size // 2), size // 2 - 2, 2)
        pygame.draw.polygon(
            surface,
            settings.COLOR_WHITE,
            [(size // 2, size // 4), (size // 2 + 6, size // 2 + 4), (size // 2 - 6, size // 2 + 4)],
        )
        return surface

    def update(self) -> None:
        """Langsam nach unten fallen; außerhalb des Bildschirms entfernen."""
        self.rect.y += settings.POWERUP_SPEED
        if self.rect.top > settings.SCREEN_HEIGHT:
            self.kill()
