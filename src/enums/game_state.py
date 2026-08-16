from enum import Enum

class GameState(Enum):
    TITLE_MENU = "title_menu"
    SETTINGS_MENU = "settings_menu"
    KEYBINDS_MENU = "keybinds_menu"
    SOUND_MENU = "sound_menu"
    SAVE_FILE_MENU = "save_file_menu"
    TRACK_SELECTION_MENU = "track_selection_menu"
    VEHICLE_SELECTION_MENU = "vehicle_selection_menu"
    DIFFICULTY_SELECTION_MENU = "difficulty_selection_menu"
    RACE_MENU = "race_menu"
