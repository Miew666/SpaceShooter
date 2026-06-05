"""Zentrale Spielklasse — Schleife, Spawning, Kollisionen und UI."""

import random

import pygame

import settings
from enemy import ENEMY_TYPES
from player import Player
from powerup import PowerUp
from starfield import Starfield


class Game:
    """Steuert den gesamten Spielablauf."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(
            (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
        )
        pygame.display.set_caption("Space Shooter")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 28)
        self.font_large = pygame.font.SysFont(None, 48)

        self.starfield = Starfield()
        self._reset_state()

    def _reset_state(self) -> None:
        """Spielzustand für Neustart zurücksetzen."""
        self.player = Player()
        self.bullets = pygame.sprite.Group()
        self.enemy_lasers = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group()

        self.score = 0
        self.lives = settings.STARTING_LIVES
        self.game_over = False
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

    def _handle_events(self) -> bool:
        """Tastatur- und Fenster-Events verarbeiten. False = Spiel beenden."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and self.game_over:
                    self._reset_state()
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

    def _try_drop_powerup(self, x: int, y: int) -> None:
        """Mit 20 % Chance ein Power-Up an der Gegner-Position spawnen."""
        if random.random() < settings.POWERUP_DROP_CHANCE:
            powerup = PowerUp(x, y)
            self.powerups.add(powerup)
            self.all_sprites.add(powerup)

    def _handle_collisions(self) -> None:
        """Kollisionen zwischen Projektilen, Gegnern, Power-Ups und Spieler prüfen."""
        # Spieler-Projektil trifft Gegner
        hits = pygame.sprite.groupcollide(self.bullets, self.enemies, True, False)
        for _bullet, enemy_list in hits.items():
            for enemy in enemy_list:
                cx, cy = enemy.rect.centerx, enemy.rect.centery
                enemy.kill()
                self.score += settings.SCORE_PER_HIT
                self._try_drop_powerup(cx, cy)

        # Power-Up einsammeln — Laser-Stufe erhöhen
        collected = pygame.sprite.spritecollide(self.player, self.powerups, True)
        for _ in collected:
            self.player.upgrade_laser()

        if not self.player.is_invincible:
            # Gegner rammt Spieler
            colliding = pygame.sprite.spritecollide(
                self.player, self.enemies, False
            )
            if colliding:
                self._hit_player()
                for enemy in colliding:
                    enemy.kill()

        if not self.player.is_invincible:
            # Gegner-Schuss trifft Spieler
            laser_hits = pygame.sprite.spritecollide(
                self.player, self.enemy_lasers, True
            )
            if laser_hits:
                self._hit_player()

    def _update(self) -> None:
        """Spielzustand pro Frame aktualisieren."""
        if self.game_over:
            return

        keys = pygame.key.get_pressed()
        self.player.update(keys)

        if keys[pygame.K_SPACE]:
            new_bullets = self.player.shoot(self.bullets)
            for bullet in new_bullets:
                self.all_sprites.add(bullet)

        self.bullets.update()
        self.enemies.update()
        self.powerups.update()

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
        self.screen.blit(score_text, (10, 10))
        laser_rect = laser_text.get_rect(center=(settings.SCREEN_WIDTH // 2, 22))
        self.screen.blit(laser_text, laser_rect)
        self.screen.blit(
            lives_text,
            (settings.SCREEN_WIDTH - lives_text.get_width() - 10, 10),
        )

    def _draw_game_over(self) -> None:
        """Game-Over-Hinweis zentriert anzeigen."""
        text = self.font_large.render(
            "Game Over - Drücke R für Neustart", True, settings.COLOR_WHITE
        )
        rect = text.get_rect(center=(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2))
        self.screen.blit(text, rect)

    def _draw(self) -> None:
        """Alles auf den Bildschirm zeichnen."""
        self.screen.fill(settings.COLOR_BLACK)
        self.starfield.draw(self.screen)
        self.all_sprites.draw(self.screen)
        self.player.draw(self.screen)
        self._draw_ui()
        if self.game_over:
            self._draw_game_over()
        pygame.display.flip()

    def run(self) -> None:
        """Hauptspielschleife starten."""
        running = True
        while running:
            running = self._handle_events()
            self._update()
            self._draw()
            self.clock.tick(settings.FPS)
        pygame.quit()
