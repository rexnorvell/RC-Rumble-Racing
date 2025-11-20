import pygame

import constants


class TrackSelection:
    """Handles the track selection screen"""

    def __init__(self, screen, save_manager) -> None:
        self.screen: pygame.Surface = screen
        self.save_manager = save_manager

        # Load Images
        self.track_selection_default_image: pygame.Surface = pygame.image.load(
            constants.TRACK_SELECTION_IMAGE_PATH.format(image_name="default")).convert()
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
        self.hover_sound.set_volume(0.1)

    def handle_events(self, events, mouse_pos: tuple[int, int]) -> str:
        """Handles events like button presses"""

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
        self.screen.blit(self.current_image, (0, 0))

        # Draw locks on locked tracks
        for btn in self.buttons:
            if not self.save_manager.is_track_unlocked(btn["track"]):
                # Draw a semi-transparent overlay
                overlay = pygame.Surface((btn["rect"].width, btn["rect"].height), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 180))  # Dark overlay
                self.screen.blit(overlay, btn["rect"])

                # Draw Locked Text
                lock_surf = self.button_font.render("LOCKED", True, (200, 0, 0))
                lock_rect = lock_surf.get_rect(center=btn["rect"].center)
                self.screen.blit(lock_surf, lock_rect)

        # Determine exit button color
        if self.last_hovered == 4:
            exit_color = constants.TRACK_SELECTION_EXIT_HOVER_COLOR
        else:
            exit_color = constants.TRACK_SELECTION_EXIT_COLOR

        # Draw the exit button text
        exit_text_surf = self.button_font.render("Exit", True, exit_color)
        exit_text_rect = exit_text_surf.get_rect(center=self.exit_button_rect.center)
        self.screen.blit(exit_text_surf, exit_text_rect)