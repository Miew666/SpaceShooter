"""Zentrale Spielkonstanten — hier Balance-Werte anpassen, ohne Game-Logik zu ändern."""

# Fenster
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Farben (RGB)
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_GRAY = (180, 180, 180)
COLOR_PLAYER = (50, 150, 255)
COLOR_PLAYER_ACCENT = (200, 230, 255)
COLOR_ENEMY = (220, 50, 50)
COLOR_ENEMY_ACCENT = (255, 120, 120)
COLOR_BULLET = (255, 255, 80)

# Gegner-Projektile — Grunt (rot, geradeaus)
COLOR_GRUNT_LASER = (220, 50, 50)
GRUNT_LASER_SPEED = 6
GRUNT_LASER_WIDTH = 5
GRUNT_LASER_HEIGHT = 14
GRUNT_SHOOT_MS = 2000

# Sniper (gelb, gezielt, schnell)
COLOR_SNIPER_BEAM = (255, 255, 80)
SNIPER_BEAM_SPEED = 9
SNIPER_BEAM_WIDTH = 3
SNIPER_BEAM_HEIGHT = 18
SNIPER_SHOOT_MS = 4000

# Scatter (violett, Fächer, langsam)
COLOR_SCATTER_ORB = (120, 80, 255)
SCATTER_ORB_SPEED = 4
SCATTER_ORB_SIZE = 10
SCATTER_FAN_ANGLE = 22  # Grad links/rechts vom Mittelstrahl
SCATTER_SHOOT_MS = 3000

# Gegner-Farben (Schiff-Grafik)
COLOR_SNIPER = (50, 200, 80)
COLOR_SNIPER_ACCENT = (150, 255, 150)
COLOR_SCATTER = (100, 60, 200)
COLOR_SCATTER_ACCENT = (180, 140, 255)

# Spieler
PLAYER_SPEED = 5
PLAYER_WIDTH = 40
PLAYER_HEIGHT = 30
STARTING_LIVES = 3
INVINCIBILITY_MS = 1500  # Unverwundbarkeit nach Treffer (Millisekunden)

# Projektile
BULLET_SPEED = 10
BULLET_WIDTH = 4
BULLET_HEIGHT = 12
BULLET_COOLDOWN = 250  # Mindestabstand zwischen Schüssen (Millisekunden)

# Gegner
ENEMY_SPEED = 2
ENEMY_WIDTH = 36
ENEMY_HEIGHT = 28
ENEMY_SPAWN_INTERVAL = 2000  # Zeit zwischen Gegner-Wellen (Millisekunden)
ENEMIES_PER_WAVE = 4

# Punkte
SCORE_PER_HIT = 10

# Sternenhintergrund
STAR_COUNT = 120
