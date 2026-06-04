"""Zentrale Spielklasse — Schleife, Spawning, Kollisionen und UI."""

import pygame

import settings
from enemy import Enemy
from player import Player
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
        self.enemies = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group()

        self.score = 0
        self.lives = settings.STARTING_LIVES
        self.game_over = False
        self._last_spawn = pygame.time.get_ticks()

        # Start-Horde sofort spawnen
        self._spawn_enemies()

    def _spawn_enemies(self) -> None:
        """Neue Gegner-Welle am oberen Bildschirmrand erzeugen."""
        for _ in range(settings.ENEMIES_PER_WAVE):
            enemy = Enemy.spawn_at_top()
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

    def _handle_collisions(self) -> None:
        """Kollisionen zwischen Projektilen, Gegnern und Spieler prüfen."""
        # Projektil trifft Gegner — beide zerstören, Score erhöhen
        hits = pygame.sprite.groupcollide(
            self.bullets, self.enemies, True, True
        )
        self.score += len(hits) * settings.SCORE_PER_HIT

        # Gegner rammt Spieler — Leben verlieren (wenn nicht unverwundbar)
        if not self.player.is_invincible:
            colliding = pygame.sprite.spritecollide(
                self.player, self.enemies, False
            )
            if colliding:
                self.lives -= 1
                self.player.make_invincible()
                # Getroffene Gegner entfernen, damit kein sofortiger Re-Ram
                for enemy in colliding:
                    enemy.kill()

                if self.lives <= 0:
                    self.game_over = True

    def _update(self) -> None:
        """Spielzustand pro Frame aktualisieren."""
        if self.game_over:
            return

        keys = pygame.key.get_pressed()
        self.player.update(keys)

        if keys[pygame.K_SPACE]:
            bullet = self.player.shoot(self.bullets)
            if bullet is not None:
                self.all_sprites.add(bullet)

        self.bullets.update()
        self.enemies.update()

        # Spawn-Timer für neue Gegner-Wellen
        now = pygame.time.get_ticks()
        if now - self._last_spawn >= settings.ENEMY_SPAWN_INTERVAL:
            self._spawn_enemies()
            self._last_spawn = now

        self._handle_collisions()

    def _draw_ui(self) -> None:
        """Score und Leben oben auf dem Bildschirm anzeigen."""
        score_text = self.font.render(f"Score: {self.score}", True, settings.COLOR_WHITE)
        lives_text = self.font.render(f"Leben: {self.lives}", True, settings.COLOR_WHITE)
        self.screen.blit(score_text, (10, 10))
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
