import pygame

import constants
import utilities


class TrackSelection:
    """Handles the track selection screen"""

    def __init__(self, game, screen, save_manager) -> None:

        # General
        self.name: str = "track_selection"
        self.game = game
        self.screen: pygame.Surface = screen
        self.save_manager = save_manager
        self.num_unlocked: int = self.save_manager.num_unlocked

        # Background image
        self.background_image: pygame.Surface = pygame.image.load(constants.GENERAL_IMAGE_PATH.format(name="background")).convert()
        self.background_image = pygame.transform.scale(self.background_image,(constants.WIDTH, constants.HEIGHT))

        # Track button rects
        button_width: int = 380
        button_height: int = 213
        
        # First track
        self.first_default_image: pygame.Surface = utilities.load_image(
            constants.TRACK_SELECTION_IMAGE_PATH.format(number=1, type="default"), True, button_width, button_height)
        self.first_hover_image: pygame.Surface = utilities.load_image(
            constants.TRACK_SELECTION_IMAGE_PATH.format(number=1, type="hover"), True, button_width, button_height)

        # Second track
        self.second_default_image: pygame.Surface = utilities.load_image(
            constants.TRACK_SELECTION_IMAGE_PATH.format(number=2, type="default"), True, button_width, button_height)
        self.second_hover_image: pygame.Surface = utilities.load_image(
            constants.TRACK_SELECTION_IMAGE_PATH.format(number=2, type="hover"), True, button_width, button_height)
        self.second_locked_image: pygame.Surface = utilities.load_image(
            constants.TRACK_SELECTION_IMAGE_PATH.format(number=2, type="locked"), True, button_width, button_height)

        # Third track
        self.third_default_image: pygame.Surface = utilities.load_image(
            constants.TRACK_SELECTION_IMAGE_PATH.format(number=3, type="default"), True, button_width, button_height)
        self.third_hover_image: pygame.Surface = utilities.load_image(
            constants.TRACK_SELECTION_IMAGE_PATH.format(number=3, type="hover"), True, button_width, button_height)
        self.third_locked_image: pygame.Surface = utilities.load_image(
            constants.TRACK_SELECTION_IMAGE_PATH.format(number=3, type="locked"), True, button_width, button_height)

        # Fourth track
        self.fourth_default_image: pygame.Surface = utilities.load_image(
            constants.TRACK_SELECTION_IMAGE_PATH.format(number=4, type="default"), True, button_width, button_height)
        self.fourth_hover_image: pygame.Surface = utilities.load_image(
            constants.TRACK_SELECTION_IMAGE_PATH.format(number=4, type="hover"), True, button_width, button_height)
        self.fourth_locked_image: pygame.Surface = utilities.load_image(
            constants.TRACK_SELECTION_IMAGE_PATH.format(number=4, type="locked"), True, button_width, button_height)

        # Back Button
        self.back_button_x: int = 10
        self.back_button_width: int = 100
        self.back_button_height: int = self.back_button_width
        self.back_button_y: int = constants.HEIGHT - self.back_button_height - self.back_button_x
        self.back_default_image: pygame.Surface = utilities.load_image(
            constants.GENERAL_IMAGE_PATH.format(name="arrow_left_default"), True, self.back_button_width,
            self.back_button_height)
        self.back_hover_image: pygame.Surface = utilities.load_image(
            constants.GENERAL_IMAGE_PATH.format(name="arrow_left_hover"), True, self.back_button_width,
            self.back_button_height)
        self.back_button_rect: pygame.Rect = pygame.Rect(self.back_button_x, self.back_button_y, self.back_button_width,
                                                         self.back_button_height)
        self.back_current_image: pygame.Surface = self.back_default_image

        self.nothing_hovered_index: int = -1
        self.last_hovered_index: int = self.nothing_hovered_index
        self.back_button_index: int = 4

        # Initialize images
        self.first_image: pygame.Surface = self.first_default_image
        self.second_image: pygame.Surface = self.second_default_image
        self.third_image: pygame.Surface = self.third_default_image
        self.fourth_image: pygame.Surface = self.fourth_default_image
        self.set_current_images(self.nothing_hovered_index)

        # Store buttons with their associated track names
        self.buttons = [
            {
                "rect": pygame.Rect(302, 160, button_width, button_height),
                "track": constants.TRACK_NAMES[0],
                "index": 0
            },
            {
                "rect": pygame.Rect(727, 160, button_width, button_height),
                "track": constants.TRACK_NAMES[1],
                "index": 1
            },
            {
                "rect": pygame.Rect(302, 420, button_width, button_height),
                "track": constants.TRACK_NAMES[2],
                "index": 2
            },
            {
                "rect": pygame.Rect(727, 420, button_width, button_height),
                "track": constants.TRACK_NAMES[3],
                "index": 3
            }
        ]

        self.hover_sound: pygame.mixer.Sound = pygame.mixer.Sound(constants.HOVER_SOUND_PATH)
        self.hover_sound.set_volume(self.save_manager.get_volumes()["sfx"])

        # Transitions
        self.transitioning: bool = False
        self.transitioning_from_prev: bool = False
        self.transitioning_to_prev: bool = False
        self.transitioning_to_next: bool = False
        self.transitioning_from_next: bool = False
        self.transition_start_time_ms: int = 0
        self.transition_prev_duration_ms: int = 400
        self.transition_prev_pause_time: int = 400
        self.transition_next_duration_ms: int = 400
        self.transition_next_pause_time: int = 400

    def handle_events(self, events, mouse_pos: tuple[int, int]) -> str:
        """Handles events like button presses"""

        if self.transitioning:
            return constants.NO_ACTION_CODE

        hovered_index: int = self.nothing_hovered_index

        # Check button hovers
        for i, btn in enumerate(self.buttons):
            if btn["rect"].collidepoint(mouse_pos):
                # Only allow hovering if the track is unlocked
                if self.save_manager.is_track_unlocked(btn["track"]):
                    hovered_index = btn["index"]
                break

        # Check back button
        if hovered_index == self.nothing_hovered_index and self.back_button_rect.collidepoint(mouse_pos):
            hovered_index = self.back_button_index

        if hovered_index != self.last_hovered_index:
            self.last_hovered_index = hovered_index
            if hovered_index > self.nothing_hovered_index:
                self.hover_sound.play()
                self.set_current_images(hovered_index)
            else:
                self.set_current_images(self.nothing_hovered_index)

        for event in events:
            if event.type == pygame.QUIT:
                return constants.EXIT_GAME_CODE
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if hovered_index == self.back_button_index:
                    return constants.TITLE_SCREEN_NAME
                elif hovered_index > self.nothing_hovered_index:
                    self.game.set_track_name(self.buttons[hovered_index]["track"])
                    return constants.CAR_SELECTION_NAME

        return constants.NO_ACTION_CODE

    def set_current_images(self, hovered_index: int) -> None:
        """Sets the styles of the images based on which one is being hovered over"""
        self.first_image = self.first_default_image if hovered_index != 0 else self.first_hover_image
        if self.num_unlocked <= 1:
            self.second_image = self.second_locked_image
        elif hovered_index == 1:
            self.second_image = self.second_hover_image
        else:
            self.second_image = self.second_default_image
        
        if self.num_unlocked <= 2:
            self.third_image = self.third_locked_image
        elif hovered_index == 2:
            self.third_image = self.third_hover_image
        else:
            self.third_image = self.third_default_image
        
        if self.num_unlocked <= 3:
            self.fourth_image = self.fourth_locked_image
        elif hovered_index == 3:
            self.fourth_image = self.fourth_hover_image
        else:
            self.fourth_image = self.fourth_default_image

        self.back_current_image = self.back_default_image if hovered_index != self.back_button_index else self.back_hover_image

    def draw(self) -> None:
        """Draws the track selection screen"""
        self.screen.blit(self.background_image, (0, 0))
        if self.transitioning:
            self.handle_transitions()
        else:
            self.blit_current_images(0)

    def handle_transitions(self):
        """Handles the four kinds of transitions:
            - Transitioning from the previous screen to the current screen (self.transitioning_from_prev)
            - Transitioning from the current screen to the next screen (self.transitioning_to_next)
            - Transitioning from the current screen to the previous screen (self.transitioning_to_prev)
            - Transitioning from the next screen to the current screen (self.transitioning_from_next)
        """
        foreground_x: int = 0
        current_time: int = pygame.time.get_ticks()
        time_elapsed_ms: int = current_time - self.transition_start_time_ms

        if self.transitioning_from_prev:
            if time_elapsed_ms >= self.transition_prev_duration_ms:
                self.end_transition()
            else:
                transition_time_elapsed_ms: int = min(time_elapsed_ms, self.transition_prev_duration_ms)
                percent_progress: float = transition_time_elapsed_ms / self.transition_prev_duration_ms
                foreground_x = constants.WIDTH - int(percent_progress * constants.WIDTH)
        elif self.transitioning_to_prev:
            if time_elapsed_ms >= self.transition_prev_duration_ms:
                foreground_x = constants.WIDTH
                self.end_transition()
            else:
                transition_time_elapsed_ms: int = min(time_elapsed_ms, self.transition_prev_duration_ms)
                percent_progress: float = transition_time_elapsed_ms / self.transition_prev_duration_ms
                foreground_x = int(percent_progress * constants.WIDTH)
        self.blit_current_images(foreground_x)

        if self.transitioning_to_next or self.transitioning_from_next:
            is_over: bool = utilities.draw_garage_transition(self.screen, self.transition_start_time_ms, self.transition_next_duration_ms, self.transitioning_to_next, self.transition_next_pause_time, self.game.garage_door)
            if is_over:
                self.end_transition()

    def blit_current_images(self, x: int) -> None:
        """Draws the current images to the screen with an optional x offset"""
        self.screen.blit(self.first_image, (x + 302, 160))
        self.screen.blit(self.second_image, (x + 727, 160))
        self.screen.blit(self.third_image, (x + 302, 420))
        self.screen.blit(self.fourth_image, (x + 727, 420))
        self.screen.blit(self.back_current_image, (x + self.back_button_x, self.back_button_y))

    def initialize_transition(self, start_transition: bool, backwards: bool) -> None:
        """Set flags and store the starting time of the transition"""
        self.transition_start_time_ms: int = pygame.time.get_ticks()
        self.transitioning = True
        self.transitioning_to_prev = start_transition and backwards
        self.transitioning_from_prev = not start_transition and not backwards
        self.transitioning_to_next = start_transition and not backwards
        self.transitioning_from_next = not start_transition and backwards

    def end_transition(self) -> None:
        """Reset flags after the transition is complete"""
        self.transitioning = False
        self.transitioning_to_prev = False
        self.transitioning_from_prev = False
        self.transitioning_to_next = False
        self.transitioning_from_next = False
        self.set_current_images(self.nothing_hovered_index)