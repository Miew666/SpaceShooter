"""Spieler-Projektil — unterstützt gerade, angewinkelte und Plasmastrahl-Schüsse."""

import math

import pygame

import settings


class Bullet(pygame.sprite.Sprite):
    """Projektil des Spielers — Bewegung geradeaus oder per Winkelvektor."""

    def __init__(
        self,
        x: int,
        y: int,
        angle_deg: float = 0,
        plasma: bool = False,
    ):
        super().__init__()
        self.plasma = plasma
        self.image = self._create_image(plasma)
        self.rect = self.image.get_rect(midbottom=(x, y))

        speed = settings.PLASMA_SPEED if plasma else settings.BULLET_SPEED
        rad = math.radians(angle_deg)
        self.vx = speed * math.sin(rad)
        self.vy = -speed * math.cos(rad)

    def _create_image(self, plasma: bool) -> pygame.Surface:
        """Grafik erzeugen — später durch pygame.image.load(...) ersetzen."""
        if plasma:
            w, h = settings.PLASMA_WIDTH, settings.PLASMA_HEIGHT
            color = settings.COLOR_PLASMA
        else:
            w, h = settings.BULLET_WIDTH, settings.BULLET_HEIGHT
            color = settings.COLOR_BULLET

        surface = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(surface, color, (0, 0, w, h), border_radius=3 if plasma else 2)
        if plasma:
            pygame.draw.rect(
                surface,
                settings.COLOR_PLASMA_CORE,
                (w // 4, 0, w // 2, h),
                border_radius=2,
            )
        return surface

    @classmethod
    def with_angle(cls, x: int, y: int, angle_deg: float) -> "Bullet":
        """Projektil mit Fächer-Winkel erzeugen (0° = gerade nach oben)."""
        return cls(x, y, angle_deg=angle_deg)

    @classmethod
    def plasma_beam(cls, x: int, y: int) -> "Bullet":
        """Breiter Plasmastrahl für Laser-Stufe 5."""
        return cls(x, y, plasma=True)

    def update(self) -> None:
        """Projektil bewegen; außerhalb des Bildschirms entfernen."""
        self.rect.x += self.vx
        self.rect.y += self.vy
        if (
            self.rect.bottom < 0
            or self.rect.right < 0
            or self.rect.left > settings.SCREEN_WIDTH
        ):
            self.kill()
