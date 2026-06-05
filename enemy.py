"""Gegnerisches Raumschiff."""

import random

import pygame

import settings
from enemy_laser import EnemyLaser


class Enemy(pygame.sprite.Sprite):
    """Gegner, der von oben nach unten driftet, schießt und oben respawnt."""

    def __init__(self, x: int, y: int):
        super().__init__()
        self.image = self._create_image()
        self.rect = self.image.get_rect(topleft=(x, y))
        # Individueller Schuss-Timer — jeder Gegner schießt zu unterschiedlichen Zeiten
        self._next_shot_at = pygame.time.get_ticks() + self._random_shoot_delay()

    def _random_shoot_delay(self) -> int:
        """Zufälliges Schuss-Intervall zwischen MIN und MAX (Millisekunden)."""
        return random.randint(settings.ENEMY_SHOOT_MIN_MS, settings.ENEMY_SHOOT_MAX_MS)

    def _create_image(self) -> pygame.Surface:
        """Grafik erzeugen — später durch pygame.image.load(...) ersetzen."""
        surface = pygame.Surface(
            (settings.ENEMY_WIDTH, settings.ENEMY_HEIGHT), pygame.SRCALPHA
        )
        # Invertiertes Dreieck (Spitze nach unten)
        points = [
            (settings.ENEMY_WIDTH // 2, settings.ENEMY_HEIGHT),
            (0, 0),
            (settings.ENEMY_WIDTH, 0),
        ]
        pygame.draw.polygon(surface, settings.COLOR_ENEMY, points)
        pygame.draw.polygon(surface, settings.COLOR_ENEMY_ACCENT, points, 2)
        return surface

    @classmethod
    def spawn_at_top(cls) -> "Enemy":
        """Neuen Gegner am oberen Bildschirmrand mit zufälliger X-Position erzeugen."""
        x = random.randint(0, settings.SCREEN_WIDTH - settings.ENEMY_WIDTH)
        return cls(x, -settings.ENEMY_HEIGHT)

    def try_shoot(self, enemy_lasers: pygame.sprite.Group) -> EnemyLaser | None:
        """Schießen, wenn der individuelle Cooldown abgelaufen ist."""
        now = pygame.time.get_ticks()
        if now < self._next_shot_at:
            return None

        laser = EnemyLaser(self.rect.centerx, self.rect.bottom)
        enemy_lasers.add(laser)
        self._next_shot_at = now + self._random_shoot_delay()
        return laser

    def update(self) -> None:
        """Gegner nach unten bewegen; am unteren Rand oben neu spawnen."""
        self.rect.y += settings.ENEMY_SPEED
        if self.rect.top > settings.SCREEN_HEIGHT:
            self.rect.bottom = 0
            self.rect.x = random.randint(
                0, settings.SCREEN_WIDTH - settings.ENEMY_WIDTH
            )
