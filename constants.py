import pygame

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

# Track Selection Exit button
# We need to add a blank button UI element so it can be reusable and easier to implement new buttons.
TRACK_SELECTION_EXIT_COLOR: tuple[int, int, int] = (200, 200, 200)
TRACK_SELECTION_EXIT_HOVER_COLOR: tuple[int, int, int] = (255, 255, 0) # Yellow hover

# Track parameters
TRACK_NAMES: list[str] = ["magnificent_meadow",
                          "dusty_dunes",
                          "glistening_glacier"]
NUM_LAPS: dict[str, int] = {TRACK_NAMES[0]: 3,
                            TRACK_NAMES[1]: 3,
                            TRACK_NAMES[2]: 3}
CHECKPOINT_LOCATIONS: dict[str, pygame.Rect] = {TRACK_NAMES[0]: pygame.Rect(1200, 350, 200, 50),
                                                TRACK_NAMES[1]: pygame.Rect(565, 50, 50, 300),
                                                TRACK_NAMES[2]: pygame.Rect(0, 400, 200, 50)}
FINISH_LINE_LOCATIONS: dict[str, pygame.Rect] = {TRACK_NAMES[0]: pygame.Rect(12, 400, 180, 50),
                                                TRACK_NAMES[1]: pygame.Rect(680, 590, 50, 180),
                                                TRACK_NAMES[2]: pygame.Rect(1220, 330, 180, 50)}
TRACK_IMAGE_PATH: str = "assets/images/tracks/{track_name}/{image_type}.png"
TRACK_IMAGE_TYPES: list[str] = ["track_image", "track_image_bw"]

# Car parameters
CAR_WIDTH: int = 30
CAR_HEIGHT: int = 60
MAX_SPEED: float = 6.0
ACCELERATION: float = 0.2
FRICTION: float = 0.1
TURN_SPEED: float = 2.5
START_X: dict[str, float] = {TRACK_NAMES[0]: 100.0,
                             TRACK_NAMES[1]: 780.0,
                             TRACK_NAMES[2]: 1310.0}
START_Y: dict[str, float] = {TRACK_NAMES[0]: 500.0,
                             TRACK_NAMES[1]: 670.0,
                             TRACK_NAMES[2]: 450.0,}
START_ROTATION: dict[str, int] = {TRACK_NAMES[0]: 0,
                                  TRACK_NAMES[1]: 270,
                                  TRACK_NAMES[2]: 0}
CAR_COLOR: tuple[int, int, int] = (200, 0, 0)
CAR_IMAGE_PATH: str = "assets/images/cars/{car_type}.png"
CAR_TYPES: list[str] = ["f1_car"]

# Pause Menu
PAUSE_OVERLAY_COLOR: tuple[int, int, int, int] = (0, 0, 0, 180)
PAUSE_TITLE_COLOR: tuple[int, int, int] = (255, 255, 255)
PAUSE_BUTTON_COLOR: tuple[int, int, int] = (200, 200, 200)
PAUSE_BUTTON_HOVER_COLOR: tuple[int, int, int] = (255, 255, 0) # Yellow hover
PAUSE_BUTTON_WIDTH: int = 350
PAUSE_BUTTON_HEIGHT: int = 60
PAUSE_TITLE_Y: int = 150
PAUSE_RESUME_Y: int = 300
PAUSE_REPLAY_Y: int = 400
PAUSE_EXIT_Y: int = 500

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

# Display
TEXT_COLOR: tuple[int, int, int] = (185, 5, 5)
TEXT_FONT_PATH: str = "assets/fonts/Aldrich-Regular.ttf"
WIDTH: int = 1408
HEIGHT: int = 792
GAME_TITLE: str = "RC Rumble Racing"

# Temporary track fill colors for each map until they're updated with more info
TRACK_FILL_COLORS: dict[str, tuple[int, int, int]] = {
    TRACK_NAMES[0]: (0, 102, 0),    # Dark green for Magnificent Meadow
    TRACK_NAMES[1]: (218, 165, 32), # Sandy brown for Dusty Dunes
    TRACK_NAMES[2]: (173, 216, 230)  # Light blue for Glistening Glacier
}

# Race Over Menu
RACE_OVER_TITLE_COLOR: tuple[int, int, int] = (255, 255, 255)
RACE_OVER_BUTTON_COLOR: tuple[int, int, int] = (200, 200, 200)
RACE_OVER_BUTTON_HOVER_COLOR: tuple[int, int, int] = (255, 255, 0) # Yellow hover
RACE_OVER_BUTTON_WIDTH: int = 350
RACE_OVER_BUTTON_HEIGHT: int = 60
RACE_OVER_TITLE_Y: int = 250
RACE_OVER_RETRY_Y: int = 400
RACE_OVER_EXIT_Y: int = 500