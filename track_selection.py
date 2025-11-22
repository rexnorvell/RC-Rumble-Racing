import pygame

import constants


class TrackSelection:
    """Handles the track selection screen"""

    def __init__(self, screen, save_manager) -> None:

        # General
        self.screen: pygame.Surface = screen
        self.save_manager = save_manager
        self.num_unlocked = self.save_manager.num_unlocked

        # Background image
        self.background_image: pygame.Surface = pygame.image.load(constants.GENERAL_IMAGE_PATH.format(name="background")).convert()
        self.background_image = pygame.transform.scale(self.background_image,(constants.WIDTH, constants.HEIGHT))

        # Track button rects
        button_width: int = 380
        button_height: int = 213
        
        # First track
        self.first_default_image: pygame.Surface = pygame.image.load(constants.TRACK_SELECTION_IMAGE_PATH.format(number=1, type="default"))
        self.first_default_image = pygame.transform.scale(self.first_default_image,(button_width, button_height))
        self.first_hover_image: pygame.Surface = pygame.image.load(constants.TRACK_SELECTION_IMAGE_PATH.format(number=1, type="hover"))
        self.first_hover_image = pygame.transform.scale(self.first_hover_image, (button_width, button_height))

        # Second track
        self.second_default_image: pygame.Surface = pygame.image.load(
            constants.TRACK_SELECTION_IMAGE_PATH.format(number=2, type="default"))
        self.second_default_image = pygame.transform.scale(self.second_default_image, (button_width, button_height))
        self.second_hover_image: pygame.Surface = pygame.image.load(
            constants.TRACK_SELECTION_IMAGE_PATH.format(number=2, type="hover"))
        self.second_hover_image = pygame.transform.scale(self.second_hover_image, (button_width, button_height))
        self.second_locked_image: pygame.Surface = pygame.image.load(
            constants.TRACK_SELECTION_IMAGE_PATH.format(number=2, type="locked"))
        self.second_locked_image = pygame.transform.scale(self.second_locked_image, (button_width, button_height))

        # Third track
        self.third_default_image: pygame.Surface = pygame.image.load(
            constants.TRACK_SELECTION_IMAGE_PATH.format(number=3, type="default"))
        self.third_default_image = pygame.transform.scale(self.third_default_image,
                                                           (button_width, button_height))
        self.third_hover_image: pygame.Surface = pygame.image.load(
            constants.TRACK_SELECTION_IMAGE_PATH.format(number=3, type="hover"))
        self.third_hover_image = pygame.transform.scale(self.third_hover_image, (button_width, button_height))
        self.third_locked_image: pygame.Surface = pygame.image.load(
            constants.TRACK_SELECTION_IMAGE_PATH.format(number=3, type="locked"))
        self.third_locked_image = pygame.transform.scale(self.third_locked_image, (button_width, button_height))

        # Fourth track
        self.fourth_default_image: pygame.Surface = pygame.image.load(
            constants.TRACK_SELECTION_IMAGE_PATH.format(number=4, type="default"))
        self.fourth_default_image = pygame.transform.scale(self.fourth_default_image,
                                                          (button_width, button_height))
        self.fourth_hover_image: pygame.Surface = pygame.image.load(
            constants.TRACK_SELECTION_IMAGE_PATH.format(number=4, type="hover"))
        self.fourth_hover_image = pygame.transform.scale(self.fourth_hover_image, (button_width, button_height))
        self.fourth_locked_image: pygame.Surface = pygame.image.load(
            constants.TRACK_SELECTION_IMAGE_PATH.format(number=4, type="locked"))
        self.fourth_locked_image = pygame.transform.scale(self.fourth_locked_image, (button_width, button_height))

        # Back Button
        self.back_button_x: int = 10
        self.back_button_width: int = 100
        self.back_button_height: int = self.back_button_width
        self.back_button_y: int = constants.HEIGHT - self.back_button_height - self.back_button_x
        self.back_default_image: pygame.Surface = pygame.image.load(
            constants.GENERAL_IMAGE_PATH.format(name="arrow_left_default"))
        self.back_default_image = pygame.transform.scale(self.back_default_image,
                                                         (self.back_button_width, self.back_button_height))
        self.back_hover_image: pygame.Surface = pygame.image.load(
            constants.GENERAL_IMAGE_PATH.format(name="arrow_left_hover"))
        self.back_hover_image = pygame.transform.scale(self.back_hover_image,
                                                       (self.back_button_width, self.back_button_height))
        self.back_button_rect: pygame.Rect = pygame.Rect(self.back_button_x, self.back_button_y, self.back_button_width,
                                                         self.back_button_height)
        self.back_current_image: pygame.Surface = self.back_default_image

        # Initialize images
        self.first_image: pygame.Surface = self.first_default_image
        self.second_image: pygame.Surface = self.second_default_image
        self.third_image: pygame.Surface = self.third_default_image
        self.fourth_image: pygame.Surface = self.fourth_default_image
        self.set_track_images(0)

        # Transition
        self.garage_door: pygame.Surface = pygame.image.load(constants.GENERAL_IMAGE_PATH.format(name="garage")).convert()
        self.garage_door = pygame.transform.scale(self.garage_door,(constants.WIDTH, constants.HEIGHT))

        # Store buttons with their associated track names
        self.buttons = [
            {
                "rect": pygame.Rect(302, 160, button_width, button_height),
                "track": constants.TRACK_NAMES[0]
            },
            {
                "rect": pygame.Rect(727, 160, button_width, button_height),
                "track": constants.TRACK_NAMES[1]
            },
            {
                "rect": pygame.Rect(302, 420, button_width, button_height),
                "track": constants.TRACK_NAMES[2]
            },
            {
                "rect": pygame.Rect(727, 420, button_width, button_height),
                "track": constants.TRACK_NAMES[3]
            }
        ]

        self.last_hovered: int = 0

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
            return ""

        hovered_index: int = 0

        # Check button hovers
        for i, btn in enumerate(self.buttons):
            if btn["rect"].collidepoint(mouse_pos):
                # Only allow hovering if the track is unlocked
                if self.save_manager.is_track_unlocked(btn["track"]):
                    hovered_index = i + 1  # 1-based index for logic compatibility
                break

        # Check exit button
        if hovered_index == 0 and self.back_button_rect.collidepoint(mouse_pos):
            hovered_index = 5

        if hovered_index != self.last_hovered:
            self.last_hovered = hovered_index
            if hovered_index == 5:
                self.hover_sound.play()
                self.set_track_images(hovered_index)
            elif hovered_index > 0:
                self.hover_sound.play()
                self.set_track_images(hovered_index)
            else:
                self.set_track_images(0)

        for event in events:
            if event.type == pygame.QUIT:
                return "exit"
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if hovered_index == 5:
                    return "back"
                elif hovered_index > 0:
                    # Return the selected track name
                    return self.buttons[hovered_index - 1]["track"]

        return ""

    def set_track_images(self, hovered_index: int) -> None:
        self.first_image = self.first_default_image if hovered_index != 1 else self.first_hover_image
        if self.num_unlocked <= 1:
            self.second_image = self.second_locked_image
        elif hovered_index == 2:
            self.second_image = self.second_hover_image
        else:
            self.second_image = self.second_default_image
        
        if self.num_unlocked <= 2:
            self.third_image = self.third_locked_image
        elif hovered_index == 3:
            self.third_image = self.third_hover_image
        else:
            self.third_image = self.third_default_image
        
        if self.num_unlocked <= 3:
            self.fourth_image = self.fourth_locked_image
        elif hovered_index == 4:
            self.fourth_image = self.fourth_hover_image
        else:
            self.fourth_image = self.fourth_default_image

        self.back_current_image = self.back_default_image if hovered_index != 5 else self.back_hover_image

    def draw(self) -> None:
        """Draws the track selection screen"""
        self.screen.blit(self.background_image, (0, 0))

        # Handle transitions
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
        garage_door_y: int = 0
        draw_garage_door: bool = False
        current_time: int = pygame.time.get_ticks()
        time_elapsed_ms: int = current_time - self.transition_start_time_ms
        if self.transitioning_to_next:
            draw_garage_door = True
            if time_elapsed_ms >= self.transition_next_duration_ms + self.transition_next_pause_time:
                self.end_transition()
            else:
                transition_time_elapsed_ms: int = min(time_elapsed_ms, self.transition_next_duration_ms)
                percent_progress: float = transition_time_elapsed_ms / self.transition_next_duration_ms
                garage_door_y = int(percent_progress * constants.HEIGHT) - constants.HEIGHT
        elif self.transitioning_from_next:
            draw_garage_door = True
            if time_elapsed_ms >= self.transition_next_duration_ms:
                garage_door_y = -constants.HEIGHT
                self.end_transition()
            else:
                transition_time_elapsed_ms: int = min(time_elapsed_ms, self.transition_next_duration_ms)
                percent_progress: float = transition_time_elapsed_ms / self.transition_next_duration_ms
                garage_door_y = int(-percent_progress * constants.HEIGHT)
        elif self.transitioning_from_prev:
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
        if draw_garage_door:
            self.screen.blit(self.garage_door, (0, garage_door_y))

    def blit_current_images(self, x: int) -> None:
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