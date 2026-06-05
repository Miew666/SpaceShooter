"""Gegnerische Raumschiffe — Basisklasse und drei spezialisierte Typen."""

import random

import pygame

import settings
from assets import Assets
from enemy_projectile import GruntLaser, ScatterOrb, SniperBeam


class Enemy(pygame.sprite.Sprite):
    """Basisklasse für alle Gegner — Bewegung, Respawn und Schuss-Cooldown."""

    shoot_interval_ms: int = 2000
    shoot_jitter_ms: int = 0

    def __init__(self, x: int, y: int, ship_sprite: pygame.Surface):
        super().__init__()
        self.image = ship_sprite.copy()
        self.rect = self.image.get_rect(topleft=(x, y))
        self._next_shot_at = pygame.time.get_ticks() + self._random_shoot_delay()

    def _random_shoot_delay(self) -> int:
        """Schuss-Intervall mit optionalem Zufalls-Jitter."""
        jitter = random.randint(-self.shoot_jitter_ms, self.shoot_jitter_ms)
        return max(500, self.shoot_interval_ms + jitter)

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

    def __init__(self, x: int, y: int):
        super().__init__(x, y, Assets.enemy_grunt)

    def _create_projectiles(self, player: pygame.sprite.Sprite) -> list:
        laser = GruntLaser.from_enemy(self.rect.centerx, self.rect.bottom)
        return [laser]


class SniperEnemy(Enemy):
    """Gezielter Jäger — schießt selten, aber schnell auf den Spieler."""

    shoot_interval_ms = settings.SNIPER_SHOOT_MS
    shoot_jitter_ms = 300

    def __init__(self, x: int, y: int):
        super().__init__(x, y, Assets.enemy_sniper)

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

    def __init__(self, x: int, y: int):
        super().__init__(x, y, Assets.enemy_scatter)

    def _create_projectiles(self, player: pygame.sprite.Sprite) -> list:
        origin_x = self.rect.centerx
        origin_y = self.rect.bottom
        angles = (
            -settings.SCATTER_FAN_ANGLE,
            0,
            settings.SCATTER_FAN_ANGLE,
        )
        return [ScatterOrb.with_angle(origin_x, origin_y, angle) for angle in angles]


ENEMY_TYPES = [GruntEnemy, SniperEnemy, ScatterEnemy]
