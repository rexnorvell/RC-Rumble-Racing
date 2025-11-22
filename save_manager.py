import json
import os
from typing import List, Dict
import pygame

import constants


class SaveManager:
    """Handles saving and loading of game progress and settings"""

    def __init__(self, game=None):
        self.game = game
        self.file_path = constants.SAVE_FILE_PATH
        self.unlocked_tracks: List[str] = [constants.TRACK_NAMES[0]]  # Default first track unlocked

        # --- NEW: Settings ---
        self.key_bindings: Dict[str, int] = constants.DEFAULT_KEY_BINDINGS.copy()
        self.volume_settings: Dict[str, float] = {
            "music": constants.DEFAULT_MUSIC_VOLUME,
            "sfx": constants.DEFAULT_SFX_VOLUME
        }
        # --- End New ---

        self.load_data()

    def load_data(self):
        """Loads save data from the JSON file"""
        if not os.path.exists(self.file_path):
            self.apply_all_settings()
            return

        try:
            with open(self.file_path, 'r') as f:
                data = json.load(f)
                self.unlocked_tracks = data.get("unlocked_tracks", [constants.TRACK_NAMES[0]])

                # --- NEW: Load Settings ---
                self.key_bindings = data.get("key_bindings", constants.DEFAULT_KEY_BINDINGS.copy())
                # Ensure all keys are present
                for key, value in constants.DEFAULT_KEY_BINDINGS.items():
                    if key not in self.key_bindings:
                        self.key_bindings[key] = value

                self.volume_settings = data.get("volume_settings", {
                    "music": constants.DEFAULT_MUSIC_VOLUME,
                    "sfx": constants.DEFAULT_SFX_VOLUME
                })
                # --- End New ---

        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading save data: {e}")
            # Still apply defaults on error
            self.key_bindings = constants.DEFAULT_KEY_BINDINGS.copy()
            self.volume_settings = {
                "music": constants.DEFAULT_MUSIC_VOLUME,
                "sfx": constants.DEFAULT_SFX_VOLUME
            }

        self.apply_all_settings()

    def save_data(self):
        """Saves current progress and settings to the JSON file"""
        data = {
            "unlocked_tracks": self.unlocked_tracks,
            "key_bindings": self.key_bindings,
            "volume_settings": self.volume_settings
        }
        try:
            with open(self.file_path, 'w') as f:
                json.dump(data, f, indent=4)
        except IOError as e:
            print(f"Error saving data: {e}")

    def unlock_track(self, track_name: str):
        """Unlocks a specific track if it's not already unlocked"""
        if track_name in constants.TRACK_NAMES and track_name not in self.unlocked_tracks:
            self.unlocked_tracks.append(track_name)
            self.save_data()
            print(f"Unlocked track: {track_name}")

    def is_track_unlocked(self, track_name: str) -> bool:
        """Checks if a track is currently unlocked"""
        return track_name in self.unlocked_tracks

    def get_next_track_name(self, current_track_name: str) -> str | None:
        """Returns the name of the next track in the list, or None if last"""
        try:
            idx = constants.TRACK_NAMES.index(current_track_name)
            if idx + 1 < len(constants.TRACK_NAMES):
                return constants.TRACK_NAMES[idx + 1]
        except ValueError:
            pass
        return None

    # --- NEW: Settings Methods ---

    def get_key_bindings(self) -> Dict[str, int]:
        """Returns the current key bindings."""
        return self.key_bindings

    def get_volumes(self) -> Dict[str, float]:
        """Returns the current volume settings."""
        return self.volume_settings

    def update_key_bindings(self, new_bindings: Dict[str, int]):
        """Updates key bindings. Does not save until save_data() is called."""
        self.key_bindings = new_bindings.copy()

    def update_volumes(self, new_volumes: Dict[str, float]):
        """Updates volumes. Does not save until save_data() is called."""
        self.volume_settings = new_volumes.copy()
        self.apply_all_settings()  # Apply volumes immediately

    def apply_all_settings(self):
        """Applies all current settings to the game."""
        self.apply_volume_settings()
        # Key bindings are read live, so no "apply" needed

    def apply_volume_settings(self):
        """Applies current volume settings to all game sounds."""
        music_vol = self.volume_settings.get("music", constants.DEFAULT_MUSIC_VOLUME)
        sfx_vol = self.volume_settings.get("sfx", constants.DEFAULT_SFX_VOLUME)

        pygame.mixer.music.set_volume(music_vol)

        # Update sounds on the game object if it exists
        if self.game:
            if hasattr(self.game, 'click_sound'):
                self.game.click_sound.set_volume(sfx_vol)
            if hasattr(self.game, 'hover_sound'):
                self.game.hover_sound.set_volume(sfx_vol)

            # Update sounds on sub-screens if they exist
            if hasattr(self.game, 'title_screen') and self.game.title_screen:
                self.game.title_screen.hover_sound.set_volume(sfx_vol)
            if hasattr(self.game, 'track_selection') and self.game.track_selection:
                self.game.track_selection.hover_sound.set_volume(sfx_vol)
            if hasattr(self.game, 'car_selection') and self.game.car_selection:
                self.game.car_selection.hover_sound.set_volume(sfx_vol)
            if hasattr(self.game, 'difficulty_selection') and self.game.difficulty_selection:
                self.game.difficulty_selection.hover_sound.set_volume(sfx_vol)
            if hasattr(self.game, 'race') and self.game.race:
                self.game.race.next_lap_sound.set_volume(sfx_vol)
                self.game.race.respawn_sound.set_volume(sfx_vol)
    # --- End New ---