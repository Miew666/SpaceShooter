"""Begleit-Drohnen (Wingmen) — folgen dem Spieler und unterstützen beim Schießen."""

import pygame

import settings
from assets import Assets
from bullet import Bullet


class Drone(pygame.sprite.Sprite):
    """Mini-Drohne links oder rechts neben dem Spielerschiff."""

    # Feste Offsets relativ zum Spieler-Mittelpunkt (links, rechts)
    _SLOT_OFFSETS = (
        settings.DRONE_OFFSET_LEFT,
        settings.DRONE_OFFSET_RIGHT,
    )

    def __init__(self, player: pygame.sprite.Sprite, slot: int):
        super().__init__()
        self.player = player
        self.slot = slot
        self.offset_x, self.offset_y = self._SLOT_OFFSETS[slot]
        self.image = Assets.drone_ship.copy()
        self.rect = self.image.get_rect(center=player.rect.center)
        self._sync_position()

    def _sync_position(self) -> None:
        """Position am festen Offset zum Spieler ausrichten."""
        self.rect.midbottom = (
            self.player.rect.centerx + self.offset_x,
            self.player.rect.bottom + self.offset_y,
        )
        self.rect.left = max(0, self.rect.left)
        self.rect.right = min(settings.SCREEN_WIDTH, self.rect.right)
        self.rect.top = max(0, self.rect.top)
        self.rect.bottom = min(settings.SCREEN_HEIGHT, self.rect.bottom)

    def update(self) -> None:
        """Der Spielerbewegung mit festem Offset folgen."""
        self._sync_position()

    def shoot(self, bullet_group: pygame.sprite.Group) -> Bullet | None:
        """Kleinen Schwach-Laser geradeaus abfeuern."""
        bullet = Bullet.weak(self.rect.centerx, self.rect.top)
        bullet_group.add(bullet)
        return bullet
