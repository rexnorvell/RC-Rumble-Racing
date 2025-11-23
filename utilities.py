import sys

import pygame

import constants


def load_image(image_path: str, is_alpha: bool, width: int, height: int) -> pygame.Surface:
    """Load in and scale images"""
    image: pygame.Surface = pygame.image.load(image_path)
    image.convert_alpha() if is_alpha else image.convert()
    image = pygame.transform.scale(image, (width, height))
    return image

def quit_game() -> None:
    """Quits the game"""
    pygame.quit()
    sys.exit()

def draw_garage_transition(screen: pygame.Surface, transition_start_time_ms: int, transition_duration_ms: int, is_start: bool, transition_pause_time: int, garage_door_image: pygame.Surface) -> bool:
    """Handles the four kinds of garage transitions:
        - Transitioning from the previous screen to the current screen (self.transitioning_from_prev)
        - Transitioning from the current screen to the next screen (self.transitioning_to_next)
        - Transitioning from the current screen to the previous screen (self.transitioning_to_prev)
        - Transitioning from the next screen to the current screen (self.transitioning_from_next)
    """
    is_done: bool = False
    garage_door_y: int
    current_time: int = pygame.time.get_ticks()
    time_elapsed_ms: int = current_time - transition_start_time_ms
    transition_time_elapsed_ms: int = min(time_elapsed_ms, transition_duration_ms)
    percent_progress: float = transition_time_elapsed_ms / transition_duration_ms
    if is_start:
        pause_ms = transition_pause_time
        if time_elapsed_ms >= transition_duration_ms + pause_ms:
            garage_door_y = 0
            is_done = True
        else:
            garage_door_y = int(percent_progress * constants.HEIGHT) - constants.HEIGHT
    else:
        if time_elapsed_ms >= transition_duration_ms:
            garage_door_y = -constants.HEIGHT
            is_done = True
        else:
            garage_door_y = int(-percent_progress * constants.HEIGHT)
    screen.blit(garage_door_image, (0, garage_door_y))
    return is_done

def draw_fade_to_black_transition(screen: pygame.Surface, transition_start_time_ms: int, transition_duration_ms: int, is_start: bool, transition_pause_time: int, dark_overlay: pygame.Surface) -> bool:
    """Handles the four kinds of fade to black transitions:
            - Transitioning from the previous screen to the current screen (self.transitioning_from_prev)
            - Transitioning from the current screen to the next screen (self.transitioning_to_next)
            - Transitioning from the current screen to the previous screen (self.transitioning_to_prev)
            - Transitioning from the next screen to the current screen (self.transitioning_from_next)
        """
    is_done: bool = False
    overlay_opacity: int
    max_opacity: int = 255
    current_time: int = pygame.time.get_ticks()
    time_elapsed_ms: int = current_time - transition_start_time_ms
    transition_time_elapsed_ms: int = min(time_elapsed_ms, transition_duration_ms)
    percent_progress: float = transition_time_elapsed_ms / transition_duration_ms
    if is_start:
        pause_ms = transition_pause_time
        if time_elapsed_ms >= transition_duration_ms + pause_ms:
            overlay_opacity = max_opacity
            is_done = True
        else:
            overlay_opacity = int(percent_progress * max_opacity)
    else:
        if time_elapsed_ms >= transition_duration_ms:
            overlay_opacity = 0
            is_done = True
        else:
            overlay_opacity = max_opacity - int(percent_progress * max_opacity)
    dark_overlay.fill((0, 0, 0, overlay_opacity))
    screen.blit(dark_overlay, (0, 0))
    return is_done