import numpy as np
import numpy.typing as npt
import pygame

import constants


class Track:
    """Handles all track-related logic, images, and collision geometry."""

    def __init__(self) -> None:
        self.finish_line: pygame.Rect = pygame.Rect(12, 400, 180, 50)
        self.checkpoint_1: pygame.Rect = pygame.Rect(1200, 350, 200, 50)

        self.track_image: pygame.Surface = pygame.image.load(constants.MAGNIFICENT_MEADOW_TRACK_IMAGE).convert()
        self.track_image = pygame.transform.scale(self.track_image, (constants.WIDTH, constants.HEIGHT))

        track_image_bw: pygame.Surface = pygame.image.load(constants.MAGNIFICENT_MEADOW_TRACK_IMAGE_BW).convert()
        track_image_bw = pygame.transform.scale(track_image_bw, (constants.WIDTH, constants.HEIGHT))

        track_pixels: npt.NDArray = pygame.surfarray.array3d(track_image_bw)
        self.off_road_mask: npt.NDArray[np.bool_] = np.all(track_pixels == 255, axis=2)

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

