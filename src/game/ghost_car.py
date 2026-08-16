from __future__ import annotations

import csv
import pygame
from pathlib import Path

from game.car import Car


class GhostCar(Car):
    """
    A ghost car that strictly replays a recorded CSV path.
    No physics, no AI, just playback.
    """

    def __init__(self, screen: pygame.Surface, track_name: str, csv_path: Path, car_config: dict, style_index: int):
        # Initialize as a ghost (is_ghost=True)
        super().__init__(screen, track_name, True, car_config, style_index, {})

        self.csv_path = csv_path
        self.recording_data = []
        self.current_index = 0

        self._load_recording()

    def _load_recording(self):
        if not self.csv_path.exists():
            return

        try:
            with open(self.csv_path, newline="") as file:
                reader = csv.reader(file)
                for row in reader:
                    # CSV Format: x, y, move_angle, car_angle
                    self.recording_data.append({
                        "x": float(row[0]),
                        "y": float(row[1]),
                        "move_angle": float(row[2]),
                        "car_angle": float(row[3])
                    })
        except Exception as e:
            print(f"Error loading ghost recording: {e}")

    def update(self):
        """Updates the car's position to the next frame in the recording."""
        if not self.recording_data:
            return

        if self.current_index < len(self.recording_data):
            data = self.recording_data[self.current_index]
            self.x = data["x"]
            self.y = data["y"]
            self.move_angle = data["move_angle"]
            self.car_angle = data["car_angle"]

            # Since this is a visual replay, we set dummy speed
            # so checks (like 'is_moving') don't fail, though strictly not needed
            self.speed = 10

            self.current_index += 1
        else:
            # End of recording - stop in place
            pass

    # Override physics update to do nothing, since update() sets x/y directly
    def update_position(self):
        pass