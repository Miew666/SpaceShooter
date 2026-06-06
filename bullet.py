"""Spieler-Projektil — unterstützt gerade, angewinkelte und Plasmastrahl-Schüsse."""

import math

import pygame

import settings
from assets import Assets


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
        self.weak = False

        speed = settings.PLASMA_SPEED if plasma else settings.BULLET_SPEED
        rad = math.radians(angle_deg)
        self.vx = speed * math.sin(rad)
        self.vy = -speed * math.cos(rad)

        if plasma:
            self.image = Assets.player_plasma.copy()
        elif angle_deg == 0:
            self.image = Assets.player_laser.copy()
        else:
            self.image = Assets.rotated_player_laser(self.vx, self.vy)

        self.rect = self.image.get_rect(midbottom=(x, y))

    @classmethod
    def with_angle(cls, x: int, y: int, angle_deg: float) -> "Bullet":
        """Projektil mit Fächer-Winkel erzeugen (0° = gerade nach oben)."""
        return cls(x, y, angle_deg=angle_deg)

    @classmethod
    def plasma_beam(cls, x: int, y: int) -> "Bullet":
        """Breiter Plasmastrahl für Laser-Stufe 5."""
        return cls(x, y, plasma=True)

    @classmethod
    def weak(cls, x: int, y: int) -> "Bullet":
        """Kleiner, schwächerer Laser für Drohnen."""
        bullet = cls.__new__(cls)
        pygame.sprite.Sprite.__init__(bullet)
        bullet.plasma = False
        bullet.weak = True
        bullet.vx = 0.0
        bullet.vy = -settings.DRONE_BULLET_SPEED
        bullet.image = Assets.drone_laser.copy()
        bullet.rect = bullet.image.get_rect(midbottom=(x, y))
        return bullet

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
