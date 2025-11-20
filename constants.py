import pygame


# Display
TEXT_COLOR: tuple[int, int, int] = (185, 5, 5)
TEXT_SHADOW_COLOR: tuple[int, int, int] = (0, 0, 0)
TEXT_FONT_PATH: str = "assets/fonts/Elektrik.otf"
FALLBACK_FONT_PATH: str = "assets/fonts/60s-scoreboard.otf"
WIDTH: int = 1408
HEIGHT: int = 792
GAME_TITLE: str = "RC Rumble Racing"

# Cursor
CURSOR_IMAGE_PATH: str = "assets/images/general/cursor.png"
CURSOR_WIDTH: int = 40
CURSOR_HEIGHT: int = 40

# Title screen
TITLE_IMAGE_PATH: str = "assets/images/title_screen/{image_type}.png"
CLICK_SOUND_PATH: str = "assets/audio/general/click.mp3"
HOVER_SOUND_PATH: str = "assets/audio/general/hover.mp3"
INTRO_VIDEO_PATH: str = "assets/videos/intro.mp4"
INTRO_AUDIO_PATH: str = "assets/videos/intro.mp3"

# Track selection screen
TRACK_SELECTION_IMAGE_PATH: str = "assets/images/track_selection/{image_name}.png"

# Car selection screen
CAR_SELECTION_IMAGE_PATH: str = "assets/images/car_selection/{image_name}.png"
CAR_SELECTION_ARROW_LEFT_PATH: str = "assets/images/car_selection/arrow_left.png"
CAR_SELECTION_ARROW_RIGHT_PATH: str = "assets/images/car_selection/arrow_right.png"

# Car selection UI
CAR_STAT_BAR_COLOR: tuple[int, int, int] = (185, 5, 5) # Use main text color
CAR_STAT_BAR_BG_COLOR: tuple[int, int, int] = (50, 50, 50)
CAR_STAT_BAR_WIDTH: int = 300
CAR_STAT_BAR_HEIGHT: int = 25
CAR_STAT_MAX_VALUE: int = 10 # Stats are out of 10

# Track Selection Exit/Back button
TRACK_SELECTION_EXIT_COLOR: tuple[int, int, int] = (200, 200, 200)
TRACK_SELECTION_EXIT_HOVER_COLOR: tuple[int, int, int] = (255, 255, 0)

# Track parameters
TRACK_NAMES: list[str] = ["magnificent_meadow",
                          "dusty_dunes",
                          "glistening_glacier"]
NUM_LAPS: dict[str, int] = {TRACK_NAMES[0]: 3,
                            TRACK_NAMES[1]: 3,
                            TRACK_NAMES[2]: 3}
CHECKPOINT_LOCATIONS: dict[str, pygame.Rect] = {TRACK_NAMES[0]: pygame.Rect(1200 + (WIDTH * 0.75), 350 + (HEIGHT * 0.75), 200, 50),
                                                TRACK_NAMES[1]: pygame.Rect(565 + (WIDTH * 0.75), 50 + (HEIGHT * 0.75), 50, 300),
                                                TRACK_NAMES[2]: pygame.Rect(0 + (WIDTH * 0.75), 400 + (HEIGHT * 0.75), 200, 50)}

# Angle to face when respawning at the checkpoint
CHECKPOINT_ANGLES: dict[str, int] = {TRACK_NAMES[0]: 180,
                                     TRACK_NAMES[1]: 90,
                                     TRACK_NAMES[2]: 180}

FINISH_LINE_LOCATIONS: dict[str, pygame.Rect] = {TRACK_NAMES[0]: pygame.Rect(12 + (WIDTH * 0.75), 400 + (HEIGHT * 0.75), 180, 50),
                                                TRACK_NAMES[1]: pygame.Rect(680 + (WIDTH * 0.75), 590 + (HEIGHT * 0.75), 50, 180),
                                                TRACK_NAMES[2]: pygame.Rect(1220 + (WIDTH * 0.75), 330 + (HEIGHT * 0.75), 180, 50)}
TRACK_IMAGE_SCALE_FACTOR: dict[str, tuple[float, float]] = {TRACK_NAMES[0]: (2.5, 2.5),
                                                            TRACK_NAMES[1]: (2.5, 2.5),
                                                            TRACK_NAMES[2]: (2.5, 2.5)}
TRACK_IMAGE_PATH: str = "assets/images/tracks/{track_name}/{image_type}.png"
TRACK_IMAGE_TYPES: list[str] = ["track_image", "track_image_mask"]

# Car parameters
CAR_WIDTH: int = 30
CAR_HEIGHT: int = 60
MAX_SPEED: float = 6.0
ACCELERATION: float = 0.2
FRICTION: float = 0.1
TURN_SPEED: float = 2.5
MAX_DRIFT_ANGLE: float = 50.0
MIN_DRIFT_ANGLE: float = 15.0
DRIFT_RECOVERY_SPEED: float = 1.5
START_X: dict[str, float] = {TRACK_NAMES[0]: 100.0 + (WIDTH * 0.75),
                             TRACK_NAMES[1]: 780.0 + (WIDTH * 0.75),
                             TRACK_NAMES[2]: 1310.0 + (WIDTH * 0.75)}
START_Y: dict[str, float] = {TRACK_NAMES[0]: 500.0 + (HEIGHT * 0.75),
                             TRACK_NAMES[1]: 670.0 + (HEIGHT * 0.75),
                             TRACK_NAMES[2]: 450.0 + (HEIGHT * 0.75)}
START_ROTATION: dict[str, int] = {TRACK_NAMES[0]: 0,
                                  TRACK_NAMES[1]: 270,
                                  TRACK_NAMES[2]: 0}
CAR_COLOR: tuple[int, int, int] = (200, 0, 0)
CAR_IMAGE_PATH: str = "assets/images/cars/{car_type}.png"

# This list defines all available image files.
# The index here MUST match the index in the `styles` list below.
CAR_TYPES: list[str] = ["f1_car_red",
                        "f1_car_blue",
                        "f1_car_green",
                        "f1_car_orange"]

# This new structure defines the car properties for the selection screen
CAR_DEFINITIONS = [
    {
        "name": "F1 Racer",
        "stats": {
            "Speed": 9,
            "Acceleration": 8,
            "Handling": 7,
        },
        # These styles map to the *file names* in CAR_TYPES
        # The index (0, 1, 2, 3) will be passed to the Race class
        "styles": [
            {"name": "f1_car_red", "color": (200, 0, 0)},
            {"name": "f1_car_blue", "color": (0, 0, 200)},
            {"name": "f1_car_green", "color": (0, 200, 0)},
            {"name": "f1_car_orange", "color": (255, 165, 0)}
        ],
    },
    # When you add more cars, just add another dictionary here
    # {
    #     "name": "Rally Car",
    #     "stats": { ... },
    #     "styles": [ ... ],
    # }
]


# Pause Menu
PAUSE_MENU_IMAGE_PATH: str = "assets/images/pause/{image_name}.png"
PAUSE_OVERLAY_OPACITY: int = 100
PAUSE_TITLE_COLOR: tuple[int, int, int] = (255, 255, 255)
PAUSE_BUTTON_COLOR: tuple[int, int, int] = (200, 200, 200)
PAUSE_BUTTON_HOVER_COLOR: tuple[int, int, int] = (255, 255, 0)
PAUSE_BUTTON_WIDTH: int = 720
PAUSE_BUTTON_HEIGHT: int = 85
PAUSE_RESUME_Y: int = 288
PAUSE_REPLAY_Y: int = 419
PAUSE_EXIT_Y: int = 548

# Race Over Menu
RACE_OVER_IMAGE_PATH: str = "assets/images/race_over/{image_name}.png"
RACE_OVER_BUTTON_WIDTH: int = 720
RACE_OVER_BUTTON_HEIGHT: int = 85
RACE_OVER_RETRY_Y: int = 419
RACE_OVER_EXIT_Y: int = 548

# Replay files
REPLAY_FILE_PATH: str = "assets/replays/{track_name}/current_race.csv"
PERSONAL_BEST_FILE_PATH: str = "assets/replays/{track_name}/personal_best.csv"
PERSONAL_BEST_FILE_NAME: str = "personal_best.csv"
PERSONAL_BEST_METADATA_FILE_PATH: str = "assets/replays/{track_name}/personal_best.json"

# Ghost files
GHOST_FILE_PATH: str = "assets/ghosts/{track_name}/{difficulty}.csv"
GHOST_DIFFICULTIES: list[str] = ["easy", "medium", "hard"]

# Music and audio paths
TRACK_AUDIO_PATH: str = "assets/audio/tracks/{track_name}/{song_type}.mp3"
TRACK_SONG_TYPES: list[str] = ["track_start", "loop", "final_lap", "fast", "track_complete"]
GENERAL_AUDIO_PATH: str = "assets/audio/general/{song_name}.mp3"

# Volume settings
MUSIC_VOLUME: float = 0.5

# Map Boundaries (for respawn)
MAP_BOUNDS_BUFFER: int = 200
MAP_MIN_X: int = -MAP_BOUNDS_BUFFER
MAP_MIN_Y: int = -MAP_BOUNDS_BUFFER
MAP_MAX_X: int = WIDTH + MAP_BOUNDS_BUFFER
MAP_MAX_Y: int = HEIGHT + MAP_BOUNDS_BUFFER