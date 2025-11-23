import numpy as np
import numpy.typing as npt
import pygame

import constants


class Track:
    """Handles all track-related logic, images, and collision geometry"""

    def __init__(self, name: str) -> None:
        self.name = name

        self.finish_line: pygame.Rect = constants.FINISH_LINE_LOCATIONS[self.name]
        self.checkpoint_1: pygame.Rect = constants.CHECKPOINT_LOCATIONS[self.name]

        self.track_image: pygame.Surface = pygame.image.load(constants.TRACK_IMAGE_PATH.format(track_name=self.name, image_type=constants.TRACK_IMAGE_TYPES[0])).convert()
        self.track_image = pygame.transform.scale(self.track_image,
                                                  (constants.WIDTH * constants.TRACK_IMAGE_SCALE_FACTOR[self.name][0],
                                                   constants.HEIGHT * constants.TRACK_IMAGE_SCALE_FACTOR[self.name][1]))

        track_image_mask: pygame.Surface = pygame.image.load(constants.TRACK_IMAGE_PATH.format(track_name=self.name, image_type=constants.TRACK_IMAGE_TYPES[1])).convert()
        track_image_mask = pygame.transform.scale(track_image_mask,
                                                  (constants.WIDTH * constants.TRACK_IMAGE_SCALE_FACTOR[self.name][0],
                                                  constants.HEIGHT * constants.TRACK_IMAGE_SCALE_FACTOR[self.name][1]))

        track_pixels: npt.NDArray = pygame.surfarray.array3d(track_image_mask)
        self.off_road_mask: npt.NDArray[np.bool_] = np.all(track_pixels == 255, axis=2)
        self.out_of_bounds_mask: bool = ((track_pixels[:, :, 0] == 255) &
                                        (track_pixels[:, :, 1] == 0) &
                                        (track_pixels[:, :, 2] == 0))

        self.playlist: list[tuple[str, int]] = self._create_playlist()

    def _create_playlist(self) -> list[tuple[str, int]]:
        """Creates the playlist for the track"""
        playlist: list[tuple[str, int]] = [
            (constants.TRACK_AUDIO_PATH.format(track_name="general", song_type=constants.TRACK_SONG_TYPES[0]), 0),
            (constants.TRACK_AUDIO_PATH.format(track_name="general", song_type=constants.TRACK_SONG_TYPES[1]), 0),
            (constants.TRACK_AUDIO_PATH.format(track_name=self.name, song_type=constants.TRACK_SONG_TYPES[2]), -1),
            (constants.TRACK_AUDIO_PATH.format(track_name="general", song_type=constants.TRACK_SONG_TYPES[3]), 0),
            (constants.TRACK_AUDIO_PATH.format(track_name=self.name, song_type=constants.TRACK_SONG_TYPES[4]), -1),
            (constants.TRACK_AUDIO_PATH.format(track_name="general", song_type=constants.TRACK_SONG_TYPES[5]), 0)
        ]
        return playlist

    def draw(self, screen: pygame.Surface, camera_x: float, camera_y: float) -> None:
        """Draws the main track image onto the screen"""
        screen.blit(self.track_image, (-camera_x, -camera_y))

    def is_off_road(self, x: float, y: float) -> bool:
        """Checks if the given coordinates are off-road using the mask"""
        ix, iy = int(x), int(y)
        if 0 <= ix < self.off_road_mask.shape[0] and 0 <= iy < self.off_road_mask.shape[1]:
            return self.off_road_mask[ix, iy]
        return True  # Treat outside map boundaries as off-road

    def is_out_of_bounds(self, x: float, y: float) -> bool:
        """Checks if the given coordinates are out of bounds using the mask"""
        ix, iy = int(x), int(y)
        if 0 <= ix < self.out_of_bounds_mask.shape[0] and 0 <= iy < self.out_of_bounds_mask.shape[1]:
            return self.out_of_bounds_mask[ix, iy]
        return True  # Treat outside map boundaries as out of bounds

    def check_checkpoint(self, x: float, y: float) -> bool:
        """Checks if the given coordinates intersect the checkpoint area"""
        return self.checkpoint_1.collidepoint(int(x), int(y))

    def check_finish_line(self, x: float, y: float) -> bool:
        """Checks if the given coordinates intersect the finish line area"""
        return self.finish_line.collidepoint(int(x), int(y))