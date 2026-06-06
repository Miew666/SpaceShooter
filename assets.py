"""Zentraler Grafik-Loader — lädt, skaliert und stellt Sprites mit Fallback bereit."""

from __future__ import annotations

import math
from pathlib import Path

import pygame

import settings

# Basis-Pfad zum graphics-Ordner
GRAPHICS_DIR = Path(__file__).resolve().parent / "graphics" / "PNG"


def _load_sprite(
    relative_path: str,
    size: tuple[int, int],
    fallback_color: tuple[int, int, int],
) -> pygame.Surface:
    """Bild laden, skalieren; bei Fehler farbiges Rechteck als Fallback."""
    full_path = GRAPHICS_DIR / relative_path
    try:
        if full_path.exists():
            image = pygame.image.load(str(full_path)).convert_alpha()
            return pygame.transform.scale(image, size)
    except (pygame.error, FileNotFoundError, OSError):
        pass

    surface = pygame.Surface(size, pygame.SRCALPHA)
    pygame.draw.rect(surface, fallback_color, surface.get_rect(), border_radius=3)
    return surface


def _rotate_to_velocity(base: pygame.Surface, vx: float, vy: float) -> pygame.Surface:
    """Sprite anhand des Bewegungsvektors drehen (0° = nach oben)."""
    if vx == 0 and vy == 0:
        return base
    angle = math.degrees(math.atan2(vx, -vy))
    return pygame.transform.rotate(base, -angle)


class Assets:
    """Alle Spiel-Grafiken — einmalig via Assets.load() initialisieren."""

    _loaded = False

    # Schiffe
    player_ship: pygame.Surface
    enemy_grunt: pygame.Surface
    enemy_sniper: pygame.Surface
    enemy_scatter: pygame.Surface

    # Spieler-Projektile
    player_laser: pygame.Surface
    player_plasma: pygame.Surface

    # Gegner-Projektile
    grunt_laser: pygame.Surface
    sniper_beam: pygame.Surface
    scatter_orb: pygame.Surface

    # Power-Ups
    powerup_laser: pygame.Surface
    powerup_drone: pygame.Surface
    powerup_shield: pygame.Surface
    powerup_bomb: pygame.Surface
    powerup_magnet: pygame.Surface

    # Drohnen
    drone_ship: pygame.Surface
    drone_laser: pygame.Surface

    @classmethod
    def load(cls) -> None:
        """Alle Assets laden — in game.py nach pygame.display.set_mode() aufrufen."""
        if cls._loaded:
            return

        ship_size = (settings.PLAYER_WIDTH, settings.PLAYER_HEIGHT)
        enemy_size = (settings.ENEMY_WIDTH, settings.ENEMY_HEIGHT)

        # Spieler: blaues Raumschiff
        cls.player_ship = _load_sprite(
            "playerShip1_blue.png", ship_size, settings.COLOR_PLAYER
        )

        # Grunt: roter Standard-Gegner
        cls.enemy_grunt = _load_sprite(
            "Enemies/enemyRed1.png", enemy_size, settings.COLOR_ENEMY
        )

        # Sniper: grüner, schlanker Jäger
        cls.enemy_sniper = _load_sprite(
            "Enemies/enemyGreen2.png", enemy_size, settings.COLOR_SNIPER
        )

        # Scatter/Bomber: blauer Breitflügler
        cls.enemy_scatter = _load_sprite(
            "Enemies/enemyBlue2.png", enemy_size, settings.COLOR_SCATTER
        )

        # Spieler-Laser (blau, zeigt nach oben)
        cls.player_laser = _load_sprite(
            "Lasers/laserBlue05.png",
            (settings.BULLET_WIDTH, settings.BULLET_HEIGHT),
            settings.COLOR_BULLET,
        )

        # Plasmastrahl Stufe 5 (breiter blauer Laser)
        cls.player_plasma = _load_sprite(
            "Lasers/laserBlue16.png",
            (settings.PLASMA_WIDTH, settings.PLASMA_HEIGHT),
            settings.COLOR_PLASMA,
        )

        # Grunt-Laser (rot, zeigt nach unten)
        cls.grunt_laser = _load_sprite(
            "Lasers/laserRed05.png",
            (settings.GRUNT_LASER_WIDTH, settings.GRUNT_LASER_HEIGHT),
            settings.COLOR_GRUNT_LASER,
        )

        # Sniper-Strahl (grün, wird zur Laufzeit gedreht)
        cls.sniper_beam = _load_sprite(
            "Lasers/laserGreen07.png",
            (settings.SNIPER_BEAM_WIDTH, settings.SNIPER_BEAM_HEIGHT),
            settings.COLOR_SNIPER_BEAM,
        )

        # Scatter-Kugeln (blaue Energiekugel)
        orb_size = (settings.SCATTER_ORB_SIZE, settings.SCATTER_ORB_SIZE)
        cls.scatter_orb = _load_sprite(
            "Power-ups/powerupBlue.png", orb_size, settings.COLOR_SCATTER_ORB
        )

        # Laser-Power-Up (grüner Blitz)
        powerup_size = (settings.POWERUP_SIZE, settings.POWERUP_SIZE)
        cls.powerup_laser = _load_sprite(
            "Power-ups/powerupGreen_bolt.png", powerup_size, settings.COLOR_POWERUP
        )

        # Drohnen-Power-Up (gelbes Stern-Symbol)
        cls.powerup_drone = _load_sprite(
            "Power-ups/powerupYellow_star.png", powerup_size, settings.COLOR_DRONE
        )

        cls.powerup_shield = _load_sprite(
            "Power-ups/powerupBlue_shield.png", powerup_size, settings.COLOR_SHIELD_RING
        )

        cls.powerup_bomb = _load_sprite(
            "Power-ups/powerupRed.png", powerup_size, settings.COLOR_BOMB
        )

        cls.powerup_magnet = _load_sprite(
            "Power-ups/star_gold.png", powerup_size, settings.COLOR_MAGNET
        )

        # Mini-Drohne (kleines UFO)
        drone_size = (settings.DRONE_WIDTH, settings.DRONE_HEIGHT)
        cls.drone_ship = _load_sprite("ufoBlue.png", drone_size, settings.COLOR_DRONE)

        # Drohnen-Laser (kleiner blauer Strahl)
        cls.drone_laser = _load_sprite(
            "Lasers/laserBlue01.png",
            (settings.DRONE_BULLET_WIDTH, settings.DRONE_BULLET_HEIGHT),
            settings.COLOR_BULLET,
        )

        cls._loaded = True

    @classmethod
    def rotated_player_laser(cls, vx: float, vy: float) -> pygame.Surface:
        """Spieler-Laser für Fächer-Schüsse drehen."""
        return _rotate_to_velocity(cls.player_laser, vx, vy)

    @classmethod
    def rotated_sniper_beam(cls, vx: float, vy: float) -> pygame.Surface:
        """Sniper-Strahl in Schussrichtung drehen."""
        return _rotate_to_velocity(cls.sniper_beam, vx, vy)

    @classmethod
    def rotated_scatter_orb(cls, vx: float, vy: float) -> pygame.Surface:
        """Scatter-Kugel drehen (optional, da Kugel symmetrisch)."""
        return cls.scatter_orb
