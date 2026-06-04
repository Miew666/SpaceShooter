"""Spieler-Raumschiff."""

import pygame

import settings
from bullet import Bullet


class Player(pygame.sprite.Sprite):
    """Steuerbares Raumschiff am unteren Bildschirmrand."""

    def __init__(self):
        super().__init__()
        self.image = self._create_image()
        self.rect = self.image.get_rect(
            midbottom=(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT - 20)
        )
        self._last_shot = 0
        self.invincible_until = 0
        self._blink_visible = True
        self._blink_timer = 0

    def _create_image(self) -> pygame.Surface:
        """Grafik erzeugen — später durch pygame.image.load(...) ersetzen."""
        surface = pygame.Surface(
            (settings.PLAYER_WIDTH, settings.PLAYER_HEIGHT), pygame.SRCALPHA
        )
        # Dreieck (Spitze nach oben)
        points = [
            (settings.PLAYER_WIDTH // 2, 0),
            (0, settings.PLAYER_HEIGHT),
            (settings.PLAYER_WIDTH, settings.PLAYER_HEIGHT),
        ]
        pygame.draw.polygon(surface, settings.COLOR_PLAYER, points)
        pygame.draw.polygon(surface, settings.COLOR_PLAYER_ACCENT, points, 2)
        return surface

    @property
    def is_invincible(self) -> bool:
        """True, wenn der Spieler gerade unverwundbar ist."""
        return pygame.time.get_ticks() < self.invincible_until

    def make_invincible(self) -> None:
        """Kurze Unverwundbarkeit nach Treffer aktivieren."""
        self.invincible_until = pygame.time.get_ticks() + settings.INVINCIBILITY_MS

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

        # Blinken während Unverwundbarkeit
        if self.is_invincible:
            self._blink_timer += 1
            if self._blink_timer >= 5:
                self._blink_timer = 0
                self._blink_visible = not self._blink_visible
        else:
            self._blink_visible = True

    def shoot(self, bullet_group: pygame.sprite.Group) -> Bullet | None:
        """Projektil erzeugen, wenn Cooldown abgelaufen ist."""
        now = pygame.time.get_ticks()
        if now - self._last_shot >= settings.BULLET_COOLDOWN:
            bullet = Bullet(self.rect.centerx, self.rect.top)
            bullet_group.add(bullet)
            self._last_shot = now
            return bullet
        return None

    def draw(self, surface: pygame.Surface) -> None:
        """Spieler zeichnen (mit Blink-Effekt bei Unverwundbarkeit)."""
        if self._blink_visible:
            surface.blit(self.image, self.rect)
