import pygame

from ..enums.track_name import TrackName


# Display
TEXT_COLOR: tuple[int, int, int] = (185, 5, 5)
TEXT_SHADOW_COLOR: tuple[int, int, int] = (0, 0, 0)
TEXT_FONT_PATH: str = "assets/fonts/Elektrik.otf"
FALLBACK_FONT_PATH: str = "assets/fonts/60s-scoreboard.otf"
WIDTH: int = 1408
HEIGHT: int = 792

# Screen Names
TITLE_SCREEN_NAME: str = "title_screen"
SETTINGS_MENU_NAME: str = "settings_menu"
CONTROLS_MENU_NAME: str = "controls_menu"
SOUND_MENU_NAME: str = "sound_menu"

# Response Codes
NO_ACTION_CODE: str = ""

# Key Bindings
KEY_ACTION_FORWARD: str = "FORWARD"
KEY_ACTION_BACKWARD: str = "BACKWARD"
KEY_ACTION_LEFT: str = "LEFT"
KEY_ACTION_RIGHT: str = "RIGHT"
KEY_ACTION_DRIFT: str = "DRIFT"
KEY_ACTION_TOGGLE_GHOST: str = "TOGGLE_GHOST"

DEFAULT_KEY_BINDINGS: dict[str, int] = {
    KEY_ACTION_FORWARD: pygame.K_w,
    KEY_ACTION_BACKWARD: pygame.K_s,
    KEY_ACTION_LEFT: pygame.K_a,
    KEY_ACTION_RIGHT: pygame.K_d,
    KEY_ACTION_DRIFT: pygame.K_SPACE,
    KEY_ACTION_TOGGLE_GHOST: pygame.K_g,
}

# General
GENERAL_IMAGE_PATH: str = "assets/images/general/{name}.png"

# Track Selection Exit/Back button
TRACK_SELECTION_EXIT_COLOR: tuple[int, int, int] = (200, 200, 200)
TRACK_SELECTION_EXIT_HOVER_COLOR: tuple[int, int, int] = (255, 255, 0)

# Track parameters
TRACK_NAMES: list[str] = [TrackName.MM, TrackName.DD, TrackName.GG, TrackName.FF]

# Car parameters
CAR_WIDTH: int = 30
CAR_HEIGHT: int = 60

# Physics Base Values
BASE_MAX_SPEED: float = 4.1
SPEED_STAT_MULTIPLIER: float = 0.25
BASE_ACCELERATION: float = 0.1
ACCEL_STAT_MULTIPLIER: float = 0.015
BASE_TURN_SPEED: float = 1.5
HANDLING_STAT_MULTIPLIER: float = 0.15

# Global constants
FRICTION: float = 0.1
MAX_DRIFT_ANGLE: float = 50.0
MIN_DRIFT_ANGLE: float = 15.0
DRIFT_RECOVERY_SPEED: float = 1.5

CAR_IMAGE_PATH: str = "assets/images/cars/{car_type}.png"

# CAR DEFINITIONS
CAR_DEFINITIONS = [
    {
        "name": "Formula 1",
        "stats": { "Speed": 9, "Acceleration": 8, "Handling": 7 },
        "styles": [
            {"name": "f1_car_red", "color": (200, 0, 0)},
            {"name": "f1_car_blue", "color": (0, 0, 200)},
            {"name": "f1_car_yellow", "color": (200, 200, 0)},
            {"name": "f1_car_green", "color": (0, 200, 0)},
            {"name": "f1_car_orange", "color": (255, 128, 0)},
            {"name": "f1_car_black", "color": (0, 0, 0)},
            {"name": "f1_car_white", "color": (255, 255, 255)}
        ],
    },
    {
        "name": "Ferrari",
        "stats": { "Speed": 10, "Acceleration": 9, "Handling": 5 },
        "styles": [
            {"name": "ferrari_car_red", "color": (218, 0, 0)}
        ],
      },
    {
        "name": "Audi",
        "stats": { "Speed": 8, "Acceleration": 8, "Handling": 8 },
        "styles": [
            {"name": "audi_car_red", "color": (196, 0, 0)},
            {"name": "audi_car_sport", "color": (180, 180, 180)}
        ]
    },
    { "name": "BMW", "stats": { "Speed": 7, "Acceleration": 9, "Handling": 8 }, "styles": [{"name": "bmw_car_red", "color": (204, 0, 0)}] },
    { "name": "Chevrolet", "stats": { "Speed": 10, "Acceleration": 10, "Handling": 4 }, "styles": [{"name": "chevrolet_car_blue", "color": (0, 102, 204)}] },
    { "name": "DeLorean", "stats": { "Speed": 7, "Acceleration": 10, "Handling": 6 }, "styles": [{"name": "delorean_car_grey", "color": (132, 132, 132)}] }
]

# Replay files
REPLAY_FILE_PATH: str = "assets/replays/{track_name}/current_race.csv"
PERSONAL_BEST_METADATA_FILE_PATH: str = "assets/replays/{track_name}/personal_best.json"

# Music and audio paths
TRACK_AUDIO_PATH: str = "assets/audio/tracks/{track_name}/{song_type}.mp3"
GENERAL_AUDIO_PATH: str = "assets/audio/general/{song_name}.mp3"