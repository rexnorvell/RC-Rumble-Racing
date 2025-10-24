import pygame


# Track parameters
TRACK_NAMES: list[str] = ["magnificent_meadow",
                          "dusty_dunes"]
NUM_LAPS: dict[str, int] = {TRACK_NAMES[0]: 3,
                            TRACK_NAMES[1]: 3}
CHECKPOINT_LOCATIONS: dict[str, pygame.Rect] = {TRACK_NAMES[0]: pygame.Rect(1200, 350, 200, 50),
                                                 TRACK_NAMES[1]: pygame.Rect(565, 50, 50, 300)}
FINISH_LINE_LOCATIONS: dict[str, pygame.Rect] = {TRACK_NAMES[0]: pygame.Rect(12, 400, 180, 50),
                                                TRACK_NAMES[1]: pygame.Rect(680, 590, 50, 180)}
TRACK_IMAGE_PATH: str = "assets/tracks/"
TRACK_IMAGE_EXTENSION: str = ".png"

# Car parameters
CAR_WIDTH: int = 20
CAR_HEIGHT: int = 40
MAX_SPEED: float = 6.0
ACCELERATION: float = 0.2
FRICTION: float = 0.1
TURN_SPEED: float = 2.5
START_X: dict[str, float] = {TRACK_NAMES[0]: 100.0,
                             TRACK_NAMES[1]: 780.0}
START_Y: dict[str, float] = {TRACK_NAMES[0]: 500.0,
                             TRACK_NAMES[1]: 670.0}
START_ROTATION: dict[str, int] = {TRACK_NAMES[0]: 0,
                                  TRACK_NAMES[1]: 270}
CAR_COLOR: tuple[int, int, int] = (200, 0, 0)

# Music and audio paths
MUSIC_PATH: str = "assets/music/"
COUNTDOWN_MUSIC_EXTENSION: str = "track_start.mp3"
LOOP_MUSIC_EXTENSION: str = "_loop.mp3"
FINAL_LAP_EXTENSION: str = "final_lap.mp3"
FAST_MUSIC_EXTENSION: str = "_fast.mp3"
TRACK_COMPLETE_EXTENSION: str = "track_complete.mp3"

# Volume settings
MUSIC_VOLUME: float = 0.5

# Display
TEXT_COLOR: tuple[int, int, int] = (185, 5, 5)
TEXT_FONT_PATH: str = "assets/fonts/Elektrik.otf"
WIDTH: int = 1408
HEIGHT: int = 792
GAME_TITLE: str = "RC Rumble Racing"
