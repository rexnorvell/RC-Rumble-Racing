import json
import os
from typing import List

import constants

class SaveManager:
    """Handles saving and loading of game progress."""

    def __init__(self):
        self.file_path = constants.SAVE_FILE_PATH
        self.unlocked_tracks: List[str] = [constants.TRACK_NAMES[0]]  # Default first track unlocked
        self.load_data()

    def load_data(self):
        """Loads save data from the JSON file."""
        if not os.path.exists(self.file_path):
            return

        try:
            with open(self.file_path, 'r') as f:
                data = json.load(f)
                self.unlocked_tracks = data.get("unlocked_tracks", [constants.TRACK_NAMES[0]])
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading save data: {e}")

    def save_data(self):
        """Saves current progress to the JSON file."""
        data = {
            "unlocked_tracks": self.unlocked_tracks
        }
        try:
            with open(self.file_path, 'w') as f:
                json.dump(data, f, indent=4)
        except IOError as e:
            print(f"Error saving data: {e}")

    def unlock_track(self, track_name: str):
        """Unlocks a specific track if it's not already unlocked."""
        if track_name in constants.TRACK_NAMES and track_name not in self.unlocked_tracks:
            self.unlocked_tracks.append(track_name)
            self.save_data()
            print(f"Unlocked track: {track_name}")

    def is_track_unlocked(self, track_name: str) -> bool:
        """Checks if a track is currently unlocked."""
        return track_name in self.unlocked_tracks

    def get_next_track_name(self, current_track_name: str) -> str | None:
        """Returns the name of the next track in the list, or None if last."""
        try:
            idx = constants.TRACK_NAMES.index(current_track_name)
            if idx + 1 < len(constants.TRACK_NAMES):
                return constants.TRACK_NAMES[idx + 1]
        except ValueError:
            pass
        return None