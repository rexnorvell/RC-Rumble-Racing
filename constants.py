# Car parameters
CAR_WIDTH, CAR_HEIGHT = 20, 40
MAX_SPEED = 6
ACCELERATION = 0.2
FRICTION = 0.1
TURN_SPEED = 2.5
START_X, START_Y = 100, 500

# Track parameters
NUM_LAPS = 3
MAGNIFICENT_MEADOW_TRACK_IMAGE = "assets/tracks/magnificent_meadow.png"
MAGNIFICENT_MEADOW_TRACK_IMAGE_BW = "assets/tracks/magnificent_meadow_bw.png"

# Music
MAGNIFICENT_MEADOW_MUSIC_START = "assets/music/magnificent_meadow_start.mp3"
MAGNIFICENT_MEADOW_MUSIC_LOOP = "assets/music/magnificent_meadow_loop.mp3"
MAGNIFICENT_MEADOW_MUSIC_FAST = "assets/music/magnificent_meadow_fast.mp3"
TRACK_COMPLETE_MUSIC = "assets/music/track_complete.mp3"
MAGNIFICENT_MEADOW_PLAYLIST = [
    (MAGNIFICENT_MEADOW_MUSIC_START, 0),
    (MAGNIFICENT_MEADOW_MUSIC_LOOP, -1),
    (MAGNIFICENT_MEADOW_MUSIC_FAST, -1),
    (TRACK_COMPLETE_MUSIC, 0)
]
MUSIC_VOLUME = 0.5

# Colors
CAR_COLOR = (200, 0, 0)
TEXT_COLOR = (185, 5, 5)

# Fonts
TEXT_FONT_PATH = "assets/fonts/Elektrik.otf"

# Screen dimensions
WIDTH, HEIGHT = 1408, 792

# Title
GAME_TITLE = "RC Rumble Racing"