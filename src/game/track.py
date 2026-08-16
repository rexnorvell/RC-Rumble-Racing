from __future__ import annotations

import pygame

from utilities import constants
from enums.track_name import TrackName


class Track:
    """Handles all track-related logic, images, and collision geometry"""

    def __init__(self, name: TrackName) -> None:
        CHECKPOINT_LOCATIONS: dict[str, pygame.Rect] = {
            constants.TRACK_NAMES[0]: pygame.Rect(2256, 944, 200, 50),
            constants.TRACK_NAMES[1]: pygame.Rect(1621, 644, 50, 300),
            constants.TRACK_NAMES[2]: pygame.Rect(1056, 994, 200, 50),
            constants.TRACK_NAMES[3]: pygame.Rect(3950, 1350, 250, 50)
        }
        FINISH_LINE_LOCATIONS: dict[str, pygame.Rect] = {
            constants.TRACK_NAMES[0]: pygame.Rect(1068, 994, 180, 50),
            constants.TRACK_NAMES[1]: pygame.Rect(1736, 1184, 50, 180),
            constants.TRACK_NAMES[2]: pygame.Rect(2276, 924, 180, 50),
            constants.TRACK_NAMES[3]: pygame.Rect(675, 1176, 400, 50)
        }
        TRACK_IMAGE_SCALE_FACTOR: dict[str, tuple[float, float]] = {
            constants.TRACK_NAMES[0]: (2.5, 2.5), 
            constants.TRACK_NAMES[1]: (2.5, 2.5), 
            constants.TRACK_NAMES[2]: (2.5, 2.5), 
            constants.TRACK_NAMES[3]: (3.5, 3.5)
        }
        TRACK_IMAGE_PATH: str = "assets/images/tracks/{track_name}/{image_type}.png"
        TRACK_IMAGE_TYPES: list[str] = ["track_image", "track_image_mask"]

        self.name: TrackName = name

        self.finish_line: pygame.Rect = FINISH_LINE_LOCATIONS[self.name]
        self.checkpoint_1: pygame.Rect = CHECKPOINT_LOCATIONS[self.name]

        self.track_image: pygame.Surface = pygame.image.load(TRACK_IMAGE_PATH.format(track_name=self.name.value, image_type=TRACK_IMAGE_TYPES[0])).convert()
        self.track_image = pygame.transform.scale(self.track_image,
                                                  (constants.WIDTH * TRACK_IMAGE_SCALE_FACTOR[self.name][0],
                                                   constants.HEIGHT * TRACK_IMAGE_SCALE_FACTOR[self.name][1]))

        self.track_image_mask: pygame.Surface = pygame.image.load(TRACK_IMAGE_PATH.format(track_name=self.name.value, image_type=TRACK_IMAGE_TYPES[1])).convert()
        self.track_image_mask = pygame.transform.scale(self.track_image_mask,
                                                  (constants.WIDTH * TRACK_IMAGE_SCALE_FACTOR[self.name][0],
                                                  constants.HEIGHT * TRACK_IMAGE_SCALE_FACTOR[self.name][1]))

        self.playlist: list[tuple[str, int]] = self._create_playlist()

    def _create_playlist(self) -> list[tuple[str, int]]:
        """Creates the playlist for the track"""

        TRACK_SONG_TYPES: list[str] = ["before_race", "track_start", "loop", "final_lap", "fast", "track_complete"]

        playlist: list[tuple[str, int]] = [
            (constants.TRACK_AUDIO_PATH.format(track_name="general", song_type=TRACK_SONG_TYPES[0]), 0),
            (constants.TRACK_AUDIO_PATH.format(track_name="general", song_type=TRACK_SONG_TYPES[1]), 0),
            (constants.TRACK_AUDIO_PATH.format(track_name=self.name.value, song_type=TRACK_SONG_TYPES[2]), -1),
            (constants.TRACK_AUDIO_PATH.format(track_name="general", song_type=TRACK_SONG_TYPES[3]), 0),
            (constants.TRACK_AUDIO_PATH.format(track_name=self.name.value, song_type=TRACK_SONG_TYPES[4]), -1),
            (constants.TRACK_AUDIO_PATH.format(track_name="general", song_type=TRACK_SONG_TYPES[5]), 0)
        ]
        return playlist

    def draw(self, screen: pygame.Surface, camera_x: float, camera_y: float) -> None:
        """Draws the main track image onto the screen"""
        screen.blit(self.track_image, (-camera_x, -camera_y))

    def is_off_road(self, x: float, y: float) -> bool:
        """Checks if the given coordinates are off-road using the mask"""
        color = self.track_image_mask.get_at((int(x), int(y)))
        return color.r == 255 and color.g == 255 and color.b == 255

    def is_out_of_bounds(self, x: float, y: float) -> bool:
        """Checks if the given coordinates are out of bounds using the mask"""
        color = self.track_image_mask.get_at((int(x), int(y)))
        return color.r == 255 and color.g == 0 and color.b == 0

    def check_checkpoint(self, x: float, y: float) -> bool:
        """Checks if the given coordinates intersect the checkpoint area"""
        return self.checkpoint_1.collidepoint(int(x), int(y))

    def check_finish_line(self, x: float, y: float) -> bool:
        """Checks if the given coordinates intersect the finish line area"""
        return self.finish_line.collidepoint(int(x), int(y))