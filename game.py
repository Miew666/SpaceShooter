"""Zentrale Spielklasse — Schleife, Spawning, Kollisionen und UI."""

import asyncio
import random
import sys
import platform

import pygame

import settings
from assets import Assets
from enemy import ENEMY_TYPES
from player import Player
from particle import spawn_explosion
from powerup import PowerUp, PowerUpType
from starfield import Starfield


class Game:
    """Steuert den gesamten Spielablauf."""

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Space Shooter")

        self.web = sys.platform == "emscripten"
        display_info = pygame.display.Info()
        self.native_width = display_info.current_w
        self.native_height = display_info.current_h
        if self.web:
            self.native_width, self.native_height = 800, 600
        self.screen = pygame.display.set_mode(
            (self.native_width, self.native_height),
            pygame.RESIZABLE if self.web else pygame.FULLSCREEN,
        )

        # Virtuelle Spielfläche — Logik bleibt bei fester Auflösung
        self.game_surface = pygame.Surface(
            (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
        )
        self._compute_display_rect()

        Assets.load()
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 28)
        self.font_large = pygame.font.SysFont(None, 48)

        self.starfield = Starfield()
        self._reset_state()

    def _compute_display_rect(self) -> None:
        """Skaliertes Ziel-Rechteck berechnen — Seitenverhältnis bleibt erhalten."""
        scale = min(
            self.native_width / settings.SCREEN_WIDTH,
            self.native_height / settings.SCREEN_HEIGHT,
        )
        scaled_width = int(settings.SCREEN_WIDTH * scale)
        scaled_height = int(settings.SCREEN_HEIGHT * scale)
        offset_x = (self.native_width - scaled_width) // 2
        offset_y = (self.native_height - scaled_height) // 2
        self.display_rect = pygame.Rect(
            offset_x, offset_y, scaled_width, scaled_height
        )

    def _reset_state(self) -> None:
        """Spielzustand für Neustart zurücksetzen."""
        self.player = Player()
        self.bullets = pygame.sprite.Group()
        self.enemy_lasers = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.particles = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group()

        self.score = 0
        self.lives = settings.STARTING_LIVES
        self.game_over = False
        self.paused = self.web
        self.touch_id = None
        self.touch_position = None
        self.touch_delta = [0.0, 0.0]
        self._last_spawn = pygame.time.get_ticks()

        # Start-Horde sofort spawnen
        self._spawn_enemies()

    def _spawn_enemies(self) -> None:
        """Neue Gegner-Welle mit zufällig gemischten Typen spawnen."""
        for _ in range(settings.ENEMIES_PER_WAVE):
            enemy_cls = random.choice(ENEMY_TYPES)
            enemy = enemy_cls.spawn_at_top()
            self.enemies.add(enemy)
            self.all_sprites.add(enemy)

    def _clear_touch(self) -> None:
        self.touch_id = None
        self.touch_position = None
        self.touch_delta = [0.0, 0.0]

    def _pointer_down(self, pointer_id, position) -> None:
        if not self.display_rect.collidepoint(position):
            return
        x = (position[0] - self.display_rect.x) * settings.SCREEN_WIDTH / self.display_rect.width
        y = (position[1] - self.display_rect.y) * settings.SCREEN_HEIGHT / self.display_rect.height
        if self.game_over:
            self._reset_state()
            self.paused = False
            return
        if self.paused:
            self.paused = False
            self._last_spawn = pygame.time.get_ticks()
            self._clear_touch()
            return
        if pygame.Rect(680, 42, 110, 56).collidepoint(x, y):
            self.paused = True
            self._clear_touch()
            return
        if self.touch_id is None:
            self.touch_id = pointer_id
            self.touch_position = position

    def _pointer_move(self, pointer_id, position) -> None:
        if pointer_id != self.touch_id or self.touch_position is None:
            return
        self.touch_delta[0] += (position[0] - self.touch_position[0]) * settings.SCREEN_WIDTH / self.display_rect.width
        self.touch_delta[1] += (position[1] - self.touch_position[1]) * settings.SCREEN_HEIGHT / self.display_rect.height
        self.touch_position = position

    def _handle_events(self) -> bool:
        """Touch, Maus, Tastatur und Größenänderungen verarbeiten."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.VIDEORESIZE:
                self.native_width, self.native_height = max(1, event.w), max(1, event.h)
                self.screen = pygame.display.set_mode(
                    (self.native_width, self.native_height), pygame.RESIZABLE
                )
                self._compute_display_rect()
                self._clear_touch()
            elif event.type == pygame.WINDOWFOCUSLOST:
                self.paused = True
                self._clear_touch()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if not self.web:
                        return False
                    self.paused = True
                    self._clear_touch()
                elif event.key == pygame.K_r and self.game_over:
                    self._reset_state()
                    self.paused = False
                elif event.key in (pygame.K_p, pygame.K_RETURN):
                    self.paused = not self.paused
                    self._clear_touch()
            elif event.type in (pygame.FINGERDOWN, pygame.FINGERMOTION, pygame.FINGERUP):
                position = (event.x * self.native_width, event.y * self.native_height)
                if event.type == pygame.FINGERDOWN:
                    self._pointer_down(event.finger_id, position)
                elif event.type == pygame.FINGERMOTION:
                    self._pointer_move(event.finger_id, position)
                elif event.finger_id == self.touch_id:
                    self._clear_touch()
            elif not getattr(event, "touch", False):
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self._pointer_down("mouse", event.pos)
                elif event.type == pygame.MOUSEMOTION:
                    self._pointer_move("mouse", event.pos)
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    if self.touch_id == "mouse":
                        self._clear_touch()
        return True

    def _damage_player(self) -> None:
        """Spieler verliert ein Leben (nur bei Laser-Stufe 1)."""
        self.lives -= 1
        self.player.make_invincible()
        if self.lives <= 0:
            self.game_over = True

    def _hit_player(self) -> None:
        """Spieler wird getroffen — Laser-Stufe senken oder Leben verlieren."""
        if self.player.laser_level > 1:
            self.player.downgrade_laser()
            self.player.make_invincible(settings.LASER_HIT_INVINCIBILITY_MS)
        else:
            self._damage_player()

    def _try_shield_block(self) -> bool:
        """Schutzschild verbrauchen und Treffer abfangen."""
        if self.player.shield_active:
            self.player.shield_active = False
            return True
        return False

    def _pick_powerup_type(self) -> str:
        """Zufälligen Power-Up-Typ gemäß Gewichtung wählen."""
        roll = random.random()
        thresholds = [
            (PowerUpType.LASER, settings.POWERUP_WEIGHT_LASER),
            (PowerUpType.DRONE, settings.POWERUP_WEIGHT_DRONE),
            (PowerUpType.SHIELD, settings.POWERUP_WEIGHT_SHIELD),
            (PowerUpType.BOMB, settings.POWERUP_WEIGHT_BOMB),
            (PowerUpType.MAGNET, settings.POWERUP_WEIGHT_MAGNET),
        ]
        cumulative = 0.0
        for powerup_type, weight in thresholds:
            cumulative += weight
            if roll <= cumulative:
                return powerup_type
        return PowerUpType.LASER

    def _try_drop_powerup(self, x: int, y: int) -> None:
        """Mit konfigurierter Chance ein Power-Up spawnen (~5 % pro Typ im Mittel)."""
        if random.random() >= settings.POWERUP_DROP_CHANCE:
            return

        powerup = PowerUp(x, y, self._pick_powerup_type())
        self.powerups.add(powerup)
        self.all_sprites.add(powerup)

    def _apply_powerup(self, powerup: PowerUp) -> None:
        """Effekt des eingesammelten Power-Ups auslösen."""
        if powerup.type == PowerUpType.DRONE:
            self.player.add_drone()
        elif powerup.type == PowerUpType.SHIELD:
            self.player.activate_shield()
        elif powerup.type == PowerUpType.BOMB:
            self._activate_smart_bomb()
        elif powerup.type == PowerUpType.MAGNET:
            self.player.activate_magnet()
        else:
            self.player.upgrade_laser()

    def _activate_smart_bomb(self) -> None:
        """Alle Gegner und gegnerischen Projektile auf dem Bildschirm zerstören."""
        for enemy in list(self.enemies):
            cx, cy = enemy.rect.centerx, enemy.rect.centery
            self._destroy_enemy(enemy)
            self.score += settings.SCORE_PER_HIT

        for laser in list(self.enemy_lasers):
            laser.kill()

    def _destroy_enemy(self, enemy: pygame.sprite.Sprite) -> None:
        """Gegner zerstören und Partikel-Explosion an seiner Position auslösen."""
        cx, cy = enemy.rect.centerx, enemy.rect.centery
        spawn_explosion(cx, cy, self.particles)
        enemy.kill()

    def _handle_collisions(self) -> None:
        """Kollisionen zwischen Projektilen, Gegnern, Power-Ups und Spieler prüfen."""
        # Spieler-Projektil trifft Gegner
        hits = pygame.sprite.groupcollide(self.bullets, self.enemies, True, False)
        for bullet, enemy_list in hits.items():
            for enemy in enemy_list:
                cx, cy = enemy.rect.centerx, enemy.rect.centery
                self._destroy_enemy(enemy)
                if getattr(bullet, "weak", False):
                    self.score += settings.DRONE_SCORE_PER_HIT
                else:
                    self.score += settings.SCORE_PER_HIT
                self._try_drop_powerup(cx, cy)

        # Power-Ups einsammeln
        collected = pygame.sprite.spritecollide(self.player, self.powerups, True)
        for powerup in collected:
            self._apply_powerup(powerup)

        if not self.player.is_invincible:
            # Gegner rammt Spieler
            colliding = pygame.sprite.spritecollide(
                self.player, self.enemies, False
            )
            if colliding:
                if self._try_shield_block():
                    for enemy in colliding:
                        self._destroy_enemy(enemy)
                else:
                    self._hit_player()
                    for enemy in colliding:
                        self._destroy_enemy(enemy)

        if not self.player.is_invincible:
            # Gegner-Schuss trifft Spieler
            laser_hits = pygame.sprite.spritecollide(
                self.player, self.enemy_lasers, True
            )
            if laser_hits:
                if not self._try_shield_block():
                    self._hit_player()

    def _update(self) -> None:
        """Spielzustand pro Frame aktualisieren."""
        if self.game_over or self.paused:
            return

        keys = pygame.key.get_pressed()
        movement = tuple(self.touch_delta)
        self.touch_delta = [0.0, 0.0]
        self.player.update(keys, movement)

        if keys[pygame.K_SPACE] or self.touch_id is not None:
            new_bullets = self.player.shoot(self.bullets)
            for bullet in new_bullets:
                self.all_sprites.add(bullet)

        self.bullets.update()
        self.enemies.update()
        for powerup in self.powerups:
            powerup.update(self.player, self.player.magnet_active)
        self.particles.update()

        # Gegner schießen lassen (jeder Typ mit eigenem Verhalten)
        for enemy in self.enemies:
            projectiles = enemy.try_shoot(self.enemy_lasers, self.player)
            for projectile in projectiles:
                self.all_sprites.add(projectile)

        self.enemy_lasers.update()

        # Spawn-Timer für neue Gegner-Wellen
        now = pygame.time.get_ticks()
        if now - self._last_spawn >= settings.ENEMY_SPAWN_INTERVAL:
            self._spawn_enemies()
            self._last_spawn = now

        self._handle_collisions()

    def _draw_ui(self) -> None:
        """Score, Leben und Laser-Stufe oben anzeigen."""
        score_text = self.font.render(f"Score: {self.score}", True, settings.COLOR_WHITE)
        lives_text = self.font.render(f"Leben: {self.lives}", True, settings.COLOR_WHITE)
        laser_text = self.font.render(
            f"Laser: {self.player.laser_level}/{settings.MAX_LASER_LEVEL}",
            True,
            settings.COLOR_POWERUP,
        )
        drone_text = self.font.render(
            f"Drohnen: {len(self.player.drones)}/{settings.MAX_DRONES}",
            True,
            settings.COLOR_DRONE,
        )
        status_parts = []
        if self.player.shield_active:
            status_parts.append("Schild")
        if self.player.magnet_active:
            status_parts.append("Magnet")
        status_text = self.font.render(
            " | ".join(status_parts) if status_parts else "",
            True,
            settings.COLOR_WHITE,
        )
        self.game_surface.blit(score_text, (10, 10))
        laser_rect = laser_text.get_rect(center=(settings.SCREEN_WIDTH // 2, 22))
        self.game_surface.blit(laser_text, laser_rect)
        self.game_surface.blit(drone_text, (10, 36))
        if status_parts:
            self.game_surface.blit(status_text, (10, 58))
        self.game_surface.blit(
            lives_text,
            (settings.SCREEN_WIDTH - lives_text.get_width() - 10, 10),
        )

    def _draw_game_over(self) -> None:
        """Game-Over-Hinweis zentriert anzeigen."""
        text = self.font_large.render(
            "Game Over - Tippen oder R", True, settings.COLOR_WHITE
        )
        rect = text.get_rect(center=(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2))
        self.game_surface.blit(text, rect)

    def _draw(self) -> None:
        """Spiel auf virtuelle Surface zeichnen und skaliert auf Vollbild blitten."""
        self.game_surface.fill(settings.COLOR_BLACK)
        self.starfield.draw(self.game_surface)
        self.all_sprites.draw(self.game_surface)
        self.particles.draw(self.game_surface)
        self.player.draw(self.game_surface)
        self._draw_ui()
        if self.game_over:
            self._draw_game_over()
        elif self.paused:
            shade = pygame.Surface(self.game_surface.get_size(), pygame.SRCALPHA)
            shade.fill((0, 0, 0, 200))
            self.game_surface.blit(shade, (0, 0))
            for label, y in [
                ("Space Shooter - Tippen zum Spielen", 240),
                ("Finger ziehen: bewegen + feuern", 290),
                ("Pause: oben rechts | Tastatur: Pfeile, Leertaste, P", 330),
            ]:
                text = self.font.render(label, True, settings.COLOR_WHITE)
                self.game_surface.blit(text, text.get_rect(center=(400, y)))
        else:
            pygame.draw.rect(self.game_surface, (30, 50, 80), (680, 42, 110, 56), border_radius=8)
            text = self.font.render("Pause", True, settings.COLOR_WHITE)
            self.game_surface.blit(text, text.get_rect(center=(735, 70)))

        self.screen.fill(settings.COLOR_BLACK)
        scaled_surface = pygame.transform.scale(
            self.game_surface, self.display_rect.size
        )
        self.screen.blit(scaled_surface, self.display_rect.topleft)
        pygame.display.flip()
        if self.web and hasattr(platform, "window"):
            platform.window.canvas.setAttribute("aria-label", "Space Shooter Spielfeld")

    async def run(self) -> None:
        """Hauptspielschleife starten."""
        running = True
        while running:
            frame_start = pygame.time.get_ticks()
            running = self._handle_events()
            self._update()
            self._draw()
            if self.web:
                elapsed = (pygame.time.get_ticks() - frame_start) / 1000
                await asyncio.sleep(max(0, 1 / settings.FPS - elapsed))
            else:
                self.clock.tick(settings.FPS)
                await asyncio.sleep(0)
        pygame.quit()
