import json
import os
import pygame

from . import constants
from ..enums.difficulty import Difficulty
from ..enums.track_name import TrackName


class SaveManager:
    SAVE_FILE_TEMPLATE: str = "save_data_{slot}.json"
    DEFAULT_MUSIC_VOLUME: float = 0.5
    DEFAULT_SFX_VOLUME: float = 0.2

    def __init__(self, slot_index: int = 0):
        self.slot_index = slot_index
        # Convert 0-based index (0, 1, 2) to 1-based file slot (1, 2, 3)
        try:
            self.slot_num = int(slot_index) + 1
        except:
            self.slot_num = 1

        self.current_slot = self.slot_num
        self.file_path = self.SAVE_FILE_TEMPLATE.format(slot=self.slot_num)
        self.data = self._load_data()

    def set_save_slot(self, slot_index: int):
        """Switches the active save slot and reloads data."""
        try:
            self.slot_num = int(slot_index) + 1  # FIX: Add 1
        except:
            self.slot_num = 1

        self.current_slot = self.slot_num
        self.file_path = self.SAVE_FILE_TEMPLATE.format(slot=self.slot_num)
        self.data = self._load_data()
        self.apply_all_settings()

    def delete_save_data(self, slot_index: int):
        """Deletes the save file for the specified slot index."""
        try:
            target_file_num = int(slot_index) + 1  # FIX: Add 1
        except:
            return

        filename = self.SAVE_FILE_TEMPLATE.format(slot=target_file_num)

        if os.path.exists(filename):
            try:
                os.remove(filename)
                # If we deleted the active slot, reset memory to defaults (but don't save)
                if self.slot_num == target_file_num:
                    self.data = self._create_default_dict()
            except OSError as e:
                print(f"[SaveManager] Error deleting file: {e}")

    def _load_data(self):
        if not os.path.exists(self.file_path):
            return self._create_default_dict()
        try:
            with open(self.file_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return self._create_default_dict()

    def _create_default_dict(self):
        return {
            "unlocked_tracks": [constants.TRACK_NAMES[0].value],
            "unlocked_difficulties": {
                constants.TRACK_NAMES[0].value: [Difficulty.EASY.value],
                constants.TRACK_NAMES[1].value: [Difficulty.EASY.value],
                constants.TRACK_NAMES[2].value: [Difficulty.EASY.value],
                constants.TRACK_NAMES[3].value: [Difficulty.EASY.value]
            },
            "key_bindings": constants.DEFAULT_KEY_BINDINGS.copy(),
            "volume_settings": {"music": self.DEFAULT_MUSIC_VOLUME, "sfx": self.DEFAULT_SFX_VOLUME}
        }

    def save_data(self):
        try:
            with open(self.file_path, 'w') as f:
                json.dump(self.data, f, indent=4)
        except Exception as e:
            print(f"[SaveManager] FAIL: Could not save data! Error: {e}")

    # --- TRACKS ---
    @property
    def num_unlocked(self):
        return len(self.get_unlocked_tracks())

    def get_unlocked_tracks(self):
        return self.data.get("unlocked_tracks", [])

    def is_track_unlocked(self, track_name: TrackName) -> bool:
        return track_name.value in self.get_unlocked_tracks()

    def unlock_track(self, track_name: TrackName):
        if track_name.value not in self.data["unlocked_tracks"]:
            self.data["unlocked_tracks"].append(track_name.value)
            if "unlocked_difficulties" not in self.data:
                self.data["unlocked_difficulties"] = {}
            if track_name.value not in self.data["unlocked_difficulties"]:
                self.data["unlocked_difficulties"][track_name.value] = [Difficulty.EASY.value]
            self.save_data()

    def get_next_track_name(self, current_track_name: TrackName) -> TrackName | None:
        try:
            current_index = constants.TRACK_NAMES.index(current_track_name)
            if current_index + 1 < len(constants.TRACK_NAMES):
                return constants.TRACK_NAMES[current_index + 1]
        except ValueError:
            pass
        return None

    # --- DIFFICULTIES ---
    def is_difficulty_unlocked(self, track_name: TrackName, difficulty: Difficulty):
        if difficulty == Difficulty.EASY or difficulty == Difficulty.PB:
            return True
        unlocked = self.data.get("unlocked_difficulties", {}).get(track_name.value, [Difficulty.EASY.value])
        return difficulty.value in unlocked

    def unlock_difficulty(self, track_name: TrackName, difficulty: Difficulty):
        if "unlocked_difficulties" not in self.data:
            self.data["unlocked_difficulties"] = {}

        if track_name.value not in self.data["unlocked_difficulties"]:
            self.data["unlocked_difficulties"][track_name.value] = [Difficulty.EASY.value]

        if difficulty.value not in self.data["unlocked_difficulties"][track_name.value]:
            self.data["unlocked_difficulties"][track_name.value].append(difficulty.value)
        
        self.save_data()

    # --- SETTINGS ---
    def get_key_bindings(self):
        return self.data.get("key_bindings", constants.DEFAULT_KEY_BINDINGS)

    def set_key_binding(self, action, key):
        self.data["key_bindings"][action] = key
        self.save_data()

    def update_key_bindings(self, new_bindings):
        self.data["key_bindings"] = new_bindings

    def get_volumes(self):
        return self.data.get("volume_settings", {"music": 0.5, "sfx": 0.5})

    def update_volumes(self, new_volumes):
        self.data["volume_settings"] = new_volumes

    def set_volume(self, type_name, volume):
        self.data["volume_settings"][type_name] = volume
        self.save_data()

    # --- SAVE MANAGEMENT UI HELPERS ---
    def get_save_summary(self, slot_index: int) -> dict:
        # Convert 0-based index to 1-based file slot
        file_slot = slot_index + 1
        filename = self.SAVE_FILE_TEMPLATE.format(slot=file_slot)

        total_tracks = len(constants.TRACK_NAMES)

        if not os.path.exists(filename):
            return {
                "text": "EMPTY",
                "empty": True,
                "unlocked_tracks_count": 0,
                "completed_tracks_count": 0,
                "total_tracks_count": total_tracks
            }

        try:
            with open(filename, 'r') as f:
                data = json.load(f)

            unlocked_count = len(data.get("unlocked_tracks", []))

            # Count Completed Tracks
            completed_count = 0
            diff_map = data.get("unlocked_difficulties", {})
            for track_name in constants.TRACK_NAMES:
                unlocked_diffs = diff_map.get(track_name.value, [])
                if "complete" in unlocked_diffs:
                    completed_count += 1

            return {
                "text": "DATA FOUND",
                "empty": False,
                "unlocked_tracks_count": unlocked_count,
                "completed_tracks_count": completed_count,
                "total_tracks_count": total_tracks
            }

        except:
            return {
                "text": "CORRUPT",
                "empty": True,
                "unlocked_tracks_count": 0,
                "completed_tracks_count": 0,
                "total_tracks_count": total_tracks
            }

    def apply_all_settings(self):
        self.apply_volume_settings()

    def apply_volume_settings(self):
        volumes = self.get_volumes()
        pygame.mixer.music.set_volume(volumes.get("music", self.DEFAULT_MUSIC_VOLUME))