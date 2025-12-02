import json
import os
from typing import List, Dict
import pygame

import constants


class SaveManager:
    """Handles saving and loading of game progress and settings for a specific save slot"""

    def __init__(self, game=None):
        self.game = game
        self.current_slot: int = -1  # No slot selected by default
        self.file_path: str = ""  # Path to the current save_data_{slot}.json

        # Default values
        self.unlocked_tracks: List[str] = [constants.TRACK_NAMES[0]]  # Default first track unlocked
        self.num_unlocked: int = 1
        self.key_bindings: Dict[str, int] = constants.DEFAULT_KEY_BINDINGS.copy()
        self.volume_settings: Dict[str, float] = {
            "music": constants.DEFAULT_MUSIC_VOLUME,
            "sfx": constants.DEFAULT_SFX_VOLUME
        }

        # Do NOT load data on init. Wait for a slot to be selected.

    def set_save_slot(self, slot_index: int):
        """Sets the current save slot and loads its data."""
        if not (0 <= slot_index < constants.NUM_SAVE_SLOTS):
            return  # Invalid slot

        self.current_slot = slot_index
        self.file_path = constants.SAVE_FILE_TEMPLATE.format(slot=slot_index + 1)
        self.load_data()  # Load data from the new path

    def load_data(self):
        """Loads save data from the JSON file specified by self.file_path."""

        # Reset to defaults first
        self.unlocked_tracks: List[str] = [constants.TRACK_NAMES[0]]
        self.num_unlocked: int = 1
        self.key_bindings: Dict[str, int] = constants.DEFAULT_KEY_BINDINGS.copy()
        self.volume_settings: Dict[str, float] = {
            "music": constants.DEFAULT_MUSIC_VOLUME,
            "sfx": constants.DEFAULT_SFX_VOLUME
        }

        # If no file path is set or file doesn't exist, just apply defaults
        if not self.file_path or not os.path.exists(self.file_path):
            self.apply_all_settings()
            return

        try:
            with open(self.file_path, 'r') as f:
                data = json.load(f)
                self.unlocked_tracks = data.get("unlocked_tracks", [constants.TRACK_NAMES[0]])
            self.num_unlocked = len(self.unlocked_tracks)
            self.key_bindings = data.get("key_bindings", constants.DEFAULT_KEY_BINDINGS.copy())
            # Ensure all keys are present
            for key, value in constants.DEFAULT_KEY_BINDINGS.items():
                if key not in self.key_bindings:
                    self.key_bindings[key] = value

            self.volume_settings = data.get("volume_settings", {
                "music": constants.DEFAULT_MUSIC_VOLUME,
                "sfx": constants.DEFAULT_SFX_VOLUME
            })

        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading save data from {self.file_path}: {e}")
            # Still apply defaults on error
            self.key_bindings = constants.DEFAULT_KEY_BINDINGS.copy()
            self.volume_settings = {
                "music": constants.DEFAULT_MUSIC_VOLUME,
                "sfx": constants.DEFAULT_SFX_VOLUME
            }

        self.apply_all_settings()

    def save_data(self):
        """Saves current progress and settings to the JSON file."""
        # Do not save if no save slot is selected
        if not self.file_path:
            return

        data = {
            "unlocked_tracks": self.unlocked_tracks,
            "key_bindings": self.key_bindings,
            "volume_settings": self.volume_settings
        }
        try:
            with open(self.file_path, 'w') as f:
                json.dump(data, f, indent=4)
        except IOError as e:
            print(f"Error saving data to {self.file_path}: {e}")

    def delete_save_data(self, slot_index: int):
        """Deletes the save file for the given slot."""
        if not (0 <= slot_index < constants.NUM_SAVE_SLOTS):
            return

        file_to_delete = constants.SAVE_FILE_TEMPLATE.format(slot=slot_index + 1)
        try:
            if os.path.exists(file_to_delete):
                os.remove(file_to_delete)
        except OSError as e:
            print(f"Error deleting save file {file_to_delete}: {e}")

        # If we deleted our own active file, reset the manager
        if self.current_slot == slot_index:
            self.current_slot = -1
            self.file_path = ""
            self.load_data()  # This will reset to defaults

    def get_save_summary(self, slot_index: int) -> dict | None:
        """Checks if a save file exists and returns a brief summary. Returns None if empty."""
        if not (0 <= slot_index < constants.NUM_SAVE_SLOTS):
            return None

        file_to_check = constants.SAVE_FILE_TEMPLATE.format(slot=slot_index + 1)
        if not os.path.exists(file_to_check):
            return None

        try:
            with open(file_to_check, 'r') as f:
                data = json.load(f)
            # Provide some summary data
            unlocked = data.get("unlocked_tracks", [constants.TRACK_NAMES[0]])
            return {
                "unlocked_tracks_count": len(unlocked)
            }
        except (json.JSONDecodeError, IOError):
            return None  # File is corrupted or unreadable

    def unlock_track(self, track_name: str):
        """Unlocks a specific track if it's not already unlocked"""
        if track_name in constants.TRACK_NAMES and track_name not in self.unlocked_tracks:
            self.unlocked_tracks.append(track_name)
            self.num_unlocked = len(self.unlocked_tracks)
            self.save_data()

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

        # Sounds on the game object if it exists
        if self.game:
            if hasattr(self.game, 'click_sound'):
                self.game.click_sound.set_volume(sfx_vol)
            if hasattr(self.game, 'hover_sound'):
                self.game.hover_sound.set_volume(sfx_vol)

            # Sounds on sub-screens if they exist
            if hasattr(self.game, 'title_screen') and self.game.title_screen:
                if hasattr(self.game.title_screen, 'hover_sound'):
                    self.game.title_screen.hover_sound.set_volume(sfx_vol)

            # ADDED: Save Selection Screen
            if hasattr(self.game, 'save_selection') and self.game.save_selection:
                if hasattr(self.game.save_selection, 'hover_sound'):
                    self.game.save_selection.hover_sound.set_volume(sfx_vol)

            if hasattr(self.game, 'track_selection') and self.game.track_selection:
                if hasattr(self.game.track_selection, 'hover_sound'):
                    self.game.track_selection.hover_sound.set_volume(sfx_vol)

            if hasattr(self.game, 'car_selection') and self.game.car_selection:
                if hasattr(self.game.car_selection, 'hover_sound_nav'):
                    self.game.car_selection.hover_sound_nav.set_volume(sfx_vol)
                if hasattr(self.game.car_selection, 'hover_sound_arrow'):
                    self.game.car_selection.hover_sound_arrow.set_volume(sfx_vol)
                if hasattr(self.game.car_selection, 'select_sound_color'):
                    self.game.car_selection.select_sound_color.set_volume(sfx_vol)

            if hasattr(self.game, 'difficulty_selection') and self.game.difficulty_selection:
                if hasattr(self.game.difficulty_selection, 'hover_sound'):
                    self.game.difficulty_selection.hover_sound.set_volume(sfx_vol)

            if hasattr(self.game, 'race') and self.game.race:
                if hasattr(self.game.race, 'next_lap_sound'):
                    self.game.race.next_lap_sound.set_volume(sfx_vol)
                if hasattr(self.game.race, 'respawn_sound'):
                    self.game.race.respawn_sound.set_volume(sfx_vol)
                if hasattr(self.game.race, 'engine_idle_sound'):
                    self.game.race.engine_idle_sound.set_volume(sfx_vol)
                if hasattr(self.game.race, 'engine_off_sound'):
                    self.game.race.engine_off_sound.set_volume(sfx_vol)
                if hasattr(self.game.race, 'engine_rev_sound'):
                    self.game.race.engine_rev_sound.set_volume(sfx_vol)