"""Aufsammelbare Power-Ups — verschiedene Typen mit unterschiedlichen Effekten."""

import math

import pygame

import settings
from assets import Assets


class PowerUpType:
    """Typen von Power-Ups."""

    LASER = "laser"
    DRONE = "drone"
    SHIELD = "shield"
    BOMB = "bomb"
    MAGNET = "magnet"


# Grafik-Zuordnung pro Typ
_POWERUP_IMAGES = {
    PowerUpType.LASER: lambda: Assets.powerup_laser,
    PowerUpType.DRONE: lambda: Assets.powerup_drone,
    PowerUpType.SHIELD: lambda: Assets.powerup_shield,
    PowerUpType.BOMB: lambda: Assets.powerup_bomb,
    PowerUpType.MAGNET: lambda: Assets.powerup_magnet,
}


class PowerUp(pygame.sprite.Sprite):
    """Fällt von zerstörten Gegnern; beim Magnet-Modus zum Spieler gezogen."""

    def __init__(self, x: int, y: int, powerup_type: str = PowerUpType.LASER):
        super().__init__()
        self.type = powerup_type
        image_getter = _POWERUP_IMAGES.get(powerup_type, _POWERUP_IMAGES[PowerUpType.LASER])
        self.image = image_getter().copy()
        self.rect = self.image.get_rect(center=(x, y))

    def update(
        self,
        player: pygame.sprite.Sprite | None = None,
        magnet_active: bool = False,
    ) -> None:
        """Fallen oder zum Spieler hinbewegen (Magnet-Modus)."""
        if magnet_active and player is not None:
            self._move_toward_player(player)
        else:
            self.rect.y += settings.POWERUP_SPEED

        if self.rect.top > settings.SCREEN_HEIGHT:
            self.kill()

    def _move_toward_player(self, player: pygame.sprite.Sprite) -> None:
        """Power-Up beschleunigt auf den Spieler zu, wenn er nah genug ist."""
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        distance = math.hypot(dx, dy)

        if distance <= settings.MAGNET_RANGE:
            if distance > 0:
                pull = settings.MAGNET_PULL_SPEED
                self.rect.x += dx / distance * pull
                self.rect.y += dy / distance * pull
        else:
            self.rect.y += settings.POWERUP_SPEED
