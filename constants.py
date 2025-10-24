# Car parameters
CAR_WIDTH: int = 20
CAR_HEIGHT: int = 40
MAX_SPEED: float = 6.0
ACCELERATION: float = 0.2
FRICTION: float = 0.1
TURN_SPEED: float = 2.5
START_X: float = 100.0
START_Y: float = 500.0
CAR_COLOR: tuple[int, int, int] = (200, 0, 0)

# Track parameters
NUM_LAPS: int = 3
MAGNIFICENT_MEADOW_TRACK_IMAGE: str = "assets/tracks/magnificent_meadow.png"
MAGNIFICENT_MEADOW_TRACK_IMAGE_BW: str = "assets/tracks/magnificent_meadow_bw.png"

# Music and Audio paths
MAGNIFICENT_MEADOW_MUSIC_START: str = "assets/music/magnificent_meadow_start.mp3"
MAGNIFICENT_MEADOW_MUSIC_LOOP: str = "assets/music/magnificent_meadow_loop.mp3"
MAGNIFICENT_MEADOW_MUSIC_FAST: str = "assets/music/magnificent_meadow_fast.mp3"
TRACK_COMPLETE_MUSIC: str = "assets/music/track_complete.mp3"

# Playlist: (track_path, loop_count). 0 means play once, -1 means loop indefinitely.
MAGNIFICENT_MEADOW_PLAYLIST: list[tuple[str, int]] = [
    (MAGNIFICENT_MEADOW_MUSIC_START, 0),
    (MAGNIFICENT_MEADOW_MUSIC_LOOP, -1),
    (MAGNIFICENT_MEADOW_MUSIC_FAST, -1),
    (TRACK_COMPLETE_MUSIC, 0)
]
MUSIC_VOLUME: float = 0.5

# Display
TEXT_COLOR: tuple[int, int, int] = (185, 5, 5)
TEXT_FONT_PATH: str = "assets/fonts/Elektrik.otf"
WIDTH: int = 1408
HEIGHT: int = 792
GAME_TITLE: str = "RC Rumble Racing"
