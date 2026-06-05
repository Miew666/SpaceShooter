"""Gegner-Projektile — Basisklasse mit Geschwindigkeitsvektor und spezialisierte Typen."""

import math

import pygame

import settings


class EnemyProjectile(pygame.sprite.Sprite):
    """Basisklasse für Gegner-Schüsse — Bewegung über vx/vy-Vektor."""

    def __init__(self, x: int, y: int, vx: float, vy: float):
        super().__init__()
        self.vx = vx
        self.vy = vy
        self.image = self._create_image()
        self.rect = self.image.get_rect(center=(x, y))

    def _create_image(self) -> pygame.Surface:
        """In Unterklassen überschreiben — hier Platzhalter."""
        surface = pygame.Surface((4, 4), pygame.SRCALPHA)
        surface.fill(settings.COLOR_WHITE)
        return surface

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

    def _create_image(self) -> pygame.Surface:
        surface = pygame.Surface(
            (settings.GRUNT_LASER_WIDTH, settings.GRUNT_LASER_HEIGHT), pygame.SRCALPHA
        )
        pygame.draw.rect(
            surface,
            settings.COLOR_GRUNT_LASER,
            (0, 0, settings.GRUNT_LASER_WIDTH, settings.GRUNT_LASER_HEIGHT),
            border_radius=2,
        )
        return surface

    @classmethod
    def from_enemy(cls, x: int, y: int) -> "GruntLaser":
        """Laser mit gerader Abwärtsbewegung erzeugen."""
        return cls(x, y, 0, settings.GRUNT_LASER_SPEED)


class SniperBeam(EnemyProjectile):
    """Dünner gelber Strahl — fliegt gezielt auf den Spieler zu."""

    def _create_image(self) -> pygame.Surface:
        surface = pygame.Surface(
            (settings.SNIPER_BEAM_WIDTH, settings.SNIPER_BEAM_HEIGHT), pygame.SRCALPHA
        )
        pygame.draw.rect(
            surface,
            settings.COLOR_SNIPER_BEAM,
            (0, 0, settings.SNIPER_BEAM_WIDTH, settings.SNIPER_BEAM_HEIGHT),
            border_radius=1,
        )
        return surface

    @classmethod
    def toward_player(cls, origin_x: int, origin_y: int, target_x: int, target_y: int) -> "SniperBeam":
        """Geschwindigkeitsvektor zum Spieler berechnen und Strahl erzeugen."""
        dx = target_x - origin_x
        dy = target_y - origin_y
        length = math.hypot(dx, dy)
        if length == 0:
            vx, vy = 0.0, settings.SNIPER_BEAM_SPEED
        else:
            vx = dx / length * settings.SNIPER_BEAM_SPEED
            vy = dy / length * settings.SNIPER_BEAM_SPEED
        return cls(origin_x, origin_y, vx, vy)


class ScatterOrb(EnemyProjectile):
    """Blaue/violette Energiekugel — langsamer, im Fächer abgefeuert."""

    def _create_image(self) -> pygame.Surface:
        size = settings.SCATTER_ORB_SIZE
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(surface, settings.COLOR_SCATTER_ORB, (size // 2, size // 2), size // 2)
        return surface

    @classmethod
    def with_angle(cls, x: int, y: int, angle_deg: float) -> "ScatterOrb":
        """Kugel mit Winkel abfeuern (0° = gerade nach unten)."""
        rad = math.radians(angle_deg)
        vx = settings.SCATTER_ORB_SPEED * math.sin(rad)
        vy = settings.SCATTER_ORB_SPEED * math.cos(rad)
        return cls(x, y, vx, vy)
