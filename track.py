import numpy as np
import numpy.typing as npt
import pygame

import constants


class Track:
    """Handles all track-related logic, images, and collision geometry."""

    def __init__(self, name) -> None:
        self.name = name

        self.finish_line: pygame.Rect = constants.FINISH_LINE_LOCATIONS[self.name]
        self.checkpoint_1: pygame.Rect = constants.CHECKPOINT_LOCATIONS[self.name]

        self.track_image: pygame.Surface = pygame.image.load(constants.TRACK_IMAGE_PATH.format(track_name=self.name, image_type=constants.TRACK_IMAGE_TYPES[0])).convert()
        self.track_image = pygame.transform.scale(self.track_image, (constants.WIDTH, constants.HEIGHT))

        track_image_bw: pygame.Surface = pygame.image.load(constants.TRACK_IMAGE_PATH.format(track_name=self.name, image_type=constants.TRACK_IMAGE_TYPES[1])).convert()
        track_image_bw = pygame.transform.scale(track_image_bw, (constants.WIDTH, constants.HEIGHT))

        track_pixels: npt.NDArray = pygame.surfarray.array3d(track_image_bw)
        self.off_road_mask: npt.NDArray[np.bool_] = np.all(track_pixels == 255, axis=2)

        self.playlist = self._create_playlist()

    def _create_playlist(self) -> list[tuple[str, int]]:
        """Creates the playlist for the track."""
        playlist: list[tuple[str, int]] = [
            (constants.TRACK_AUDIO_PATH.format(track_name="general", song_type=constants.TRACK_SONG_TYPES[0]), 0),
            (constants.TRACK_AUDIO_PATH.format(track_name=self.name, song_type=constants.TRACK_SONG_TYPES[1]), -1),
            (constants.TRACK_AUDIO_PATH.format(track_name="general", song_type=constants.TRACK_SONG_TYPES[2]), 0),
            (constants.TRACK_AUDIO_PATH.format(track_name=self.name, song_type=constants.TRACK_SONG_TYPES[3]), -1),
            (constants.TRACK_AUDIO_PATH.format(track_name="general", song_type=constants.TRACK_SONG_TYPES[4]), 0)
        ]
        return playlist

    def draw(self, screen: pygame.Surface) -> None:
        """Draws the main track image onto the screen."""
        screen.blit(self.track_image, (0, 0))

    def is_off_road(self, x: float, y: float) -> bool:
        """Checks if the given coordinates are off-road using the BW mask."""
        ix, iy = int(x), int(y)
        if 0 <= ix < self.off_road_mask.shape[0] and 0 <= iy < self.off_road_mask.shape[1]:
            return self.off_road_mask[ix, iy]
        return True  # Treat outside map boundaries as off-road

    def check_checkpoint(self, x: float, y: float) -> bool:
        """Checks if the given coordinates intersect the checkpoint area."""
        return self.checkpoint_1.collidepoint(int(x), int(y))

    def check_finish_line(self, x: float, y: float) -> bool:
        """Checks if the given coordinates intersect the finish line area."""
        return self.finish_line.collidepoint(int(x), int(y))

