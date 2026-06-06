"""Partikel-Effekte — Explosionen bei zerstörten Gegnern."""

import math
import random

import pygame

import settings


class Particle(pygame.sprite.Sprite):
    """Einzelnes Explosions-Partikel — fliegt weg, verblasst und schrumpft."""

    def __init__(self, x: int, y: int):
        super().__init__()
        self.spawn_time = pygame.time.get_ticks()
        self.initial_size = random.randint(
            settings.PARTICLE_SIZE_MIN, settings.PARTICLE_SIZE_MAX
        )
        self.base_color = random.choice(settings.PARTICLE_COLORS)

        # Zufällige Richtung und Geschwindigkeit
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(
            settings.PARTICLE_SPEED_MIN, settings.PARTICLE_SPEED_MAX
        )
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed

        self.image = self._build_surface(self.initial_size, 255)
        self.rect = self.image.get_rect(center=(x, y))

    def _build_surface(self, size: int, alpha: int) -> pygame.Surface:
        """Partikel-Oberfläche mit Größe und Transparenz erzeugen."""
        size = max(1, size)
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        color = (*self.base_color, alpha)
        pygame.draw.circle(surface, color, (size // 2, size // 2), max(1, size // 2))
        return surface

    def update(self) -> None:
        """Bewegung, Verblassen und Entfernen nach Ablauf der Lebensdauer."""
        elapsed = pygame.time.get_ticks() - self.spawn_time
        if elapsed >= settings.PARTICLE_LIFETIME_MS:
            self.kill()
            return

        self.rect.x += self.vx
        self.rect.y += self.vy

        progress = elapsed / settings.PARTICLE_LIFETIME_MS
        alpha = int(255 * (1 - progress))
        size = max(1, int(self.initial_size * (1 - progress * 0.6)))

        center = self.rect.center
        self.image = self._build_surface(size, alpha)
        self.rect = self.image.get_rect(center=center)


def spawn_explosion(
    x: int, y: int, particles: pygame.sprite.Group
) -> list[Particle]:
    """15–20 Partikel an der Explosionsstelle erzeugen."""
    count = random.randint(settings.PARTICLE_COUNT_MIN, settings.PARTICLE_COUNT_MAX)
    created = []
    for _ in range(count):
        particle = Particle(x, y)
        particles.add(particle)
        created.append(particle)
    return created
