"""Gegner-Projektile — Basisklasse mit Geschwindigkeitsvektor und spezialisierte Typen."""

import math

import pygame

import settings
from assets import Assets


class EnemyProjectile(pygame.sprite.Sprite):
    """Basisklasse für Gegner-Schüsse — Bewegung über vx/vy-Vektor."""

    def __init__(self, x: int, y: int, vx: float, vy: float, image: pygame.Surface):
        super().__init__()
        self.vx = vx
        self.vy = vy
        self.image = image
        self.rect = self.image.get_rect(center=(x, y))

    def update(self) -> None:
        """Position per Geschwindigkeitsvektor aktualisieren; off-screen entfernen."""
        self.rect.x += self.vx
        self.rect.y += self.vy
        if (
            self.rect.right < 0
            or self.rect.left > settings.SCREEN_WIDTH
            or self.rect.bottom < 0
            or self.rect.top > settings.SCREEN_HEIGHT
        ):
            self.kill()


class GruntLaser(EnemyProjectile):
    """Roter Laser des Standard-Gegners — fliegt gerade nach unten."""

    @classmethod
    def from_enemy(cls, x: int, y: int) -> "GruntLaser":
        """Laser mit gerader Abwärtsbewegung erzeugen."""
        return cls(x, y, 0, settings.GRUNT_LASER_SPEED, Assets.grunt_laser.copy())


class SniperBeam(EnemyProjectile):
    """Grüner Strahl — fliegt gezielt auf den Spieler zu."""

    @classmethod
    def toward_player(
        cls, origin_x: int, origin_y: int, target_x: int, target_y: int
    ) -> "SniperBeam":
        """Geschwindigkeitsvektor zum Spieler berechnen und Strahl erzeugen."""
        dx = target_x - origin_x
        dy = target_y - origin_y
        length = math.hypot(dx, dy)
        if length == 0:
            vx, vy = 0.0, settings.SNIPER_BEAM_SPEED
        else:
            vx = dx / length * settings.SNIPER_BEAM_SPEED
            vy = dy / length * settings.SNIPER_BEAM_SPEED

        image = Assets.rotated_sniper_beam(vx, vy)
        return cls(origin_x, origin_y, vx, vy, image)


class ScatterOrb(EnemyProjectile):
    """Blaue Energiekugel — langsamer, im Fächer abgefeuert."""

    @classmethod
    def with_angle(cls, x: int, y: int, angle_deg: float) -> "ScatterOrb":
        """Kugel mit Winkel abfeuern (0° = gerade nach unten)."""
        rad = math.radians(angle_deg)
        vx = settings.SCATTER_ORB_SPEED * math.sin(rad)
        vy = settings.SCATTER_ORB_SPEED * math.cos(rad)
        return cls(x, y, vx, vy, Assets.scatter_orb.copy())
