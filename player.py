"""Spieler-Raumschiff."""

import pygame

import settings
from assets import Assets
from bullet import Bullet
from drone import Drone


class Player(pygame.sprite.Sprite):
    """Steuerbares Raumschiff am unteren Bildschirmrand."""

    def __init__(self):
        super().__init__()
        self.image = Assets.player_ship.copy()
        self.rect = self.image.get_rect(
            midbottom=(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT - 20)
        )
        self.laser_level = 1
        self.drones: list[Drone] = []
        self._last_shot = 0
        self.invincible_until = 0
        self._blink_visible = True
        self._blink_timer = 0

    @property
    def is_invincible(self) -> bool:
        """True, wenn der Spieler gerade unverwundbar ist."""
        return pygame.time.get_ticks() < self.invincible_until

    def make_invincible(self, duration_ms: int | None = None) -> None:
        """Kurze Unverwundbarkeit nach Treffer aktivieren."""
        ms = duration_ms if duration_ms is not None else settings.INVINCIBILITY_MS
        self.invincible_until = pygame.time.get_ticks() + ms

    def upgrade_laser(self) -> None:
        """Laser-Stufe um 1 erhöhen (maximal Stufe 5)."""
        self.laser_level = min(settings.MAX_LASER_LEVEL, self.laser_level + 1)

    def downgrade_laser(self) -> None:
        """Laser-Stufe um 1 senken (minimal Stufe 1)."""
        self.laser_level = max(1, self.laser_level - 1)

    def add_drone(self) -> Drone | None:
        """Neue Drohne spawnen, bis maximal zwei Begleiter."""
        if len(self.drones) >= settings.MAX_DRONES:
            return None
        drone = Drone(self, len(self.drones))
        self.drones.append(drone)
        return drone

    def update_drones(self) -> None:
        """Alle aktiven Drohnen der Spielerbewegung folgen lassen."""
        for drone in self.drones:
            drone.update()

    def _get_shoot_cooldown(self) -> int:
        """Feuerrate abhängig von der Laser-Stufe."""
        if self.laser_level >= 5:
            return settings.BULLET_COOLDOWN_L5
        if self.laser_level >= 4:
            return settings.BULLET_COOLDOWN_L4
        return settings.BULLET_COOLDOWN

    def _create_bullets_for_level(self) -> list[Bullet]:
        """Projektile gemäß aktueller Laser-Stufe erzeugen."""
        cx = self.rect.centerx
        top = self.rect.top

        if self.laser_level == 1:
            return [Bullet(cx, top)]

        if self.laser_level == 2:
            offset = settings.DUAL_SHOT_OFFSET
            return [Bullet(cx - offset, top), Bullet(cx + offset, top)]

        if self.laser_level in (3, 4):
            angles = (
                -settings.FAN_ANGLE_L3,
                0,
                settings.FAN_ANGLE_L3,
            )
            return [Bullet.with_angle(cx, top, angle) for angle in angles]

        # Stufe 5: breiter Plasmastrahl
        return [Bullet.plasma_beam(cx, top)]

    def update(self, keys: pygame.key.ScancodeWrapper) -> None:
        """Bewegung per Pfeiltasten; Position an Bildschirmränder clampen."""
        if keys[pygame.K_LEFT]:
            self.rect.x -= settings.PLAYER_SPEED
        if keys[pygame.K_RIGHT]:
            self.rect.x += settings.PLAYER_SPEED
        if keys[pygame.K_UP]:
            self.rect.y -= settings.PLAYER_SPEED
        if keys[pygame.K_DOWN]:
            self.rect.y += settings.PLAYER_SPEED

        self.rect.left = max(0, self.rect.left)
        self.rect.right = min(settings.SCREEN_WIDTH, self.rect.right)
        self.rect.top = max(0, self.rect.top)
        self.rect.bottom = min(settings.SCREEN_HEIGHT, self.rect.bottom)

        if self.is_invincible:
            self._blink_timer += 1
            if self._blink_timer >= 5:
                self._blink_timer = 0
                self._blink_visible = not self._blink_visible
        else:
            self._blink_visible = True

        self.update_drones()

    def shoot(self, bullet_group: pygame.sprite.Group) -> list[Bullet]:
        """Projektile erzeugen; Drohnen feuern mit, wenn der Spieler schießt."""
        now = pygame.time.get_ticks()
        if now - self._last_shot < self._get_shoot_cooldown():
            return []

        bullets = self._create_bullets_for_level()
        for bullet in bullets:
            bullet_group.add(bullet)

        for drone in self.drones:
            drone_bullet = drone.shoot(bullet_group)
            if drone_bullet is not None:
                bullets.append(drone_bullet)

        self._last_shot = now
        return bullets

    def draw(self, surface: pygame.Surface) -> None:
        """Drohnen und Spieler zeichnen (Blink-Effekt nur für den Spieler)."""
        for drone in self.drones:
            surface.blit(drone.image, drone.rect)
        if self._blink_visible:
            surface.blit(self.image, self.rect)
