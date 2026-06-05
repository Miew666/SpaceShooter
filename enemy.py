"""Gegnerische Raumschiffe — Basisklasse und drei spezialisierte Typen."""

import random

import pygame

import settings
from enemy_projectile import GruntLaser, ScatterOrb, SniperBeam


class Enemy(pygame.sprite.Sprite):
    """Basisklasse für alle Gegner — Bewegung, Respawn und Schuss-Cooldown."""

    # In Unterklassen überschreiben
    shoot_interval_ms: int = 2000
    shoot_jitter_ms: int = 0

    def __init__(self, x: int, y: int):
        super().__init__()
        self.image = self._create_image()
        self.rect = self.image.get_rect(topleft=(x, y))
        self._next_shot_at = pygame.time.get_ticks() + self._random_shoot_delay()

    def _random_shoot_delay(self) -> int:
        """Schuss-Intervall mit optionalem Zufalls-Jitter."""
        jitter = random.randint(-self.shoot_jitter_ms, self.shoot_jitter_ms)
        return max(500, self.shoot_interval_ms + jitter)

    def _create_image(self) -> pygame.Surface:
        """Grafik erzeugen — in Unterklassen überschreiben."""
        raise NotImplementedError

    @classmethod
    def spawn_at_top(cls) -> "Enemy":
        """Neuen Gegner am oberen Bildschirmrand mit zufälliger X-Position erzeugen."""
        x = random.randint(0, settings.SCREEN_WIDTH - settings.ENEMY_WIDTH)
        return cls(x, -settings.ENEMY_HEIGHT)

    def _create_projectiles(self, player: pygame.sprite.Sprite) -> list:
        """Projektile erzeugen — in Unterklassen implementieren."""
        raise NotImplementedError

    def try_shoot(
        self, enemy_lasers: pygame.sprite.Group, player: pygame.sprite.Sprite
    ) -> list:
        """Schießen, wenn Cooldown abgelaufen; Projektile zur Group hinzufügen."""
        now = pygame.time.get_ticks()
        if now < self._next_shot_at:
            return []

        projectiles = self._create_projectiles(player)
        for projectile in projectiles:
            enemy_lasers.add(projectile)
        self._next_shot_at = now + self._random_shoot_delay()
        return projectiles

    def update(self) -> None:
        """Gegner nach unten bewegen; am unteren Rand oben neu spawnen."""
        self.rect.y += settings.ENEMY_SPEED
        if self.rect.top > settings.SCREEN_HEIGHT:
            self.rect.bottom = 0
            self.rect.x = random.randint(
                0, settings.SCREEN_WIDTH - settings.ENEMY_WIDTH
            )


class GruntEnemy(Enemy):
    """Standard-Gegner — schießt rote Laser gerade nach unten."""

    shoot_interval_ms = settings.GRUNT_SHOOT_MS
    shoot_jitter_ms = 200

    def _create_image(self) -> pygame.Surface:
        surface = pygame.Surface(
            (settings.ENEMY_WIDTH, settings.ENEMY_HEIGHT), pygame.SRCALPHA
        )
        points = [
            (settings.ENEMY_WIDTH // 2, settings.ENEMY_HEIGHT),
            (0, 0),
            (settings.ENEMY_WIDTH, 0),
        ]
        pygame.draw.polygon(surface, settings.COLOR_ENEMY, points)
        pygame.draw.polygon(surface, settings.COLOR_ENEMY_ACCENT, points, 2)
        return surface

    def _create_projectiles(self, player: pygame.sprite.Sprite) -> list:
        laser = GruntLaser.from_enemy(self.rect.centerx, self.rect.bottom)
        return [laser]


class SniperEnemy(Enemy):
    """Gezielter Jäger — schießt selten, aber schnell auf den Spieler."""

    shoot_interval_ms = settings.SNIPER_SHOOT_MS
    shoot_jitter_ms = 300

    def _create_image(self) -> pygame.Surface:
        surface = pygame.Surface(
            (settings.ENEMY_WIDTH, settings.ENEMY_HEIGHT), pygame.SRCALPHA
        )
        # Schmale grüne Raute
        cx, cy = settings.ENEMY_WIDTH // 2, settings.ENEMY_HEIGHT // 2
        points = [(cx, 0), (settings.ENEMY_WIDTH, cy), (cx, settings.ENEMY_HEIGHT), (0, cy)]
        pygame.draw.polygon(surface, settings.COLOR_SNIPER, points)
        pygame.draw.polygon(surface, settings.COLOR_SNIPER_ACCENT, points, 2)
        return surface

    def _create_projectiles(self, player: pygame.sprite.Sprite) -> list:
        beam = SniperBeam.toward_player(
            self.rect.centerx,
            self.rect.bottom,
            player.rect.centerx,
            player.rect.centery,
        )
        return [beam]


class ScatterEnemy(Enemy):
    """Sperrfeuer-Schiff — feuert 3 Kugeln im Fächer ab."""

    shoot_interval_ms = settings.SCATTER_SHOOT_MS
    shoot_jitter_ms = 400

    def _create_image(self) -> pygame.Surface:
        surface = pygame.Surface(
            (settings.ENEMY_WIDTH, settings.ENEMY_HEIGHT), pygame.SRCALPHA
        )
        w, h = settings.ENEMY_WIDTH, settings.ENEMY_HEIGHT
        # Breiteres lila Schiff (breiteres Dreieck)
        points = [(w // 2, h), (0, h // 3), (w, h // 3)]
        pygame.draw.polygon(surface, settings.COLOR_SCATTER, points)
        pygame.draw.polygon(surface, settings.COLOR_SCATTER_ACCENT, points, 2)
        return surface

    def _create_projectiles(self, player: pygame.sprite.Sprite) -> list:
        origin_x = self.rect.centerx
        origin_y = self.rect.bottom
        angles = (
            -settings.SCATTER_FAN_ANGLE,
            0,
            settings.SCATTER_FAN_ANGLE,
        )
        return [ScatterOrb.with_angle(origin_x, origin_y, angle) for angle in angles]


# Alle spawnbaren Gegnertypen — in game.py für zufälliges Spawning nutzen
ENEMY_TYPES = [GruntEnemy, SniperEnemy, ScatterEnemy]
