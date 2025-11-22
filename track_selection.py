import pygame

import constants


class TrackSelection:
    """Handles the track selection screen"""

    def __init__(self, screen, save_manager) -> None:
        self.screen: pygame.Surface = screen
        self.save_manager = save_manager

        # Background image
        self.background_image: pygame.Surface = pygame.image.load(constants.GENERAL_IMAGE_PATH.format(name="background")).convert()
        self.background_image = pygame.transform.scale(self.background_image,(constants.WIDTH, constants.HEIGHT))

        # Load Images
        self.track_selection_default_image: pygame.Surface = pygame.image.load(
            constants.TRACK_SELECTION_IMAGE_PATH.format(image_name="default")).convert_alpha()
        self.track_selection_default_image = pygame.transform.scale(self.track_selection_default_image,
                                                                    (constants.WIDTH, constants.HEIGHT))
        self.track_selection_hover_1_image: pygame.Surface = pygame.image.load(
            constants.TRACK_SELECTION_IMAGE_PATH.format(image_name="1")).convert()
        self.track_selection_hover_1_image = pygame.transform.scale(self.track_selection_hover_1_image,
                                                                    (constants.WIDTH, constants.HEIGHT))
        self.track_selection_hover_2_image: pygame.Surface = pygame.image.load(
            constants.TRACK_SELECTION_IMAGE_PATH.format(image_name="2")).convert()
        self.track_selection_hover_2_image = pygame.transform.scale(self.track_selection_hover_2_image,
                                                                    (constants.WIDTH, constants.HEIGHT))
        self.track_selection_hover_3_image: pygame.Surface = pygame.image.load(
            constants.TRACK_SELECTION_IMAGE_PATH.format(image_name="3")).convert()
        self.track_selection_hover_3_image = pygame.transform.scale(self.track_selection_hover_3_image,
                                                                    (constants.WIDTH, constants.HEIGHT))
        self.current_image: pygame.Surface = self.track_selection_default_image
        self.garage_door: pygame.Surface = pygame.image.load(constants.GENERAL_IMAGE_PATH.format(name="garage")).convert()
        self.garage_door = pygame.transform.scale(self.garage_door,(constants.WIDTH, constants.HEIGHT))

        # Track button rects
        button_width: int = 380
        button_height: int = 213
        # Store buttons with their associated track names and images
        self.buttons = [
            {
                "rect": pygame.Rect(302, 160, button_width, button_height),
                "track": constants.TRACK_NAMES[0],
                "img": self.track_selection_hover_1_image
            },
            {
                "rect": pygame.Rect(727, 160, button_width, button_height),
                "track": constants.TRACK_NAMES[1],
                "img": self.track_selection_hover_2_image
            },
            {
                "rect": pygame.Rect(302, 420, button_width, button_height),
                "track": constants.TRACK_NAMES[2],
                "img": self.track_selection_hover_3_image
            }
        ]

        # Exit Button
        self.button_font: pygame.font.Font = pygame.font.Font(constants.TEXT_FONT_PATH, 40)
        self.exit_button_rect: pygame.Rect = pygame.Rect(20, constants.HEIGHT - 70, 150, 50)

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
        if hovered_index == 0 and self.exit_button_rect.collidepoint(mouse_pos):
            hovered_index = 4

        if hovered_index != self.last_hovered:
            self.last_hovered = hovered_index
            if hovered_index == 4:
                self.hover_sound.play()
                self.current_image = self.track_selection_default_image
            elif hovered_index > 0:
                self.hover_sound.play()
                # -1 because list is 0-indexed but hovered_index is 1-based here
                self.current_image = self.buttons[hovered_index - 1]["img"]
            else:
                self.current_image = self.track_selection_default_image

        for event in events:
            if event.type == pygame.QUIT:
                return "exit"
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if hovered_index == 4:
                    return "exit"
                elif hovered_index > 0:
                    # Return the selected track name
                    return self.buttons[hovered_index - 1]["track"]

        return ""

    def draw(self) -> None:
        """Draws the track selection screen"""
        self.screen.blit(self.background_image, (0, 0))

        # Handle transitions
        if self.transitioning:
            self.handle_transitions()
        else:
            self.screen.blit(self.current_image, (0, 0))

        # Determine exit button color
        if self.last_hovered == 4:
            exit_color = constants.TRACK_SELECTION_EXIT_HOVER_COLOR
        else:
            exit_color = constants.TRACK_SELECTION_EXIT_COLOR

        # Draw the exit button text
        exit_text_surf = self.button_font.render("Exit", True, exit_color)
        exit_text_rect = exit_text_surf.get_rect(center=self.exit_button_rect.center)
        self.screen.blit(exit_text_surf, exit_text_rect)

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
        self.screen.blit(self.current_image, (foreground_x, 0))
        if draw_garage_door:
            self.screen.blit(self.garage_door, (0, garage_door_y))

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