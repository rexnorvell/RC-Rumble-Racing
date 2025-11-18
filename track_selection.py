import pygame

import constants


class TrackSelection:
    """Handles the track selection screen"""

    def __init__(self, screen) -> None:
        self.screen: pygame.Surface = screen

        self.track_selection_default_image: pygame.Surface = pygame.image.load(constants.TRACK_SELECTION_IMAGE_PATH.format(image_name="default")).convert()
        self.track_selection_default_image = pygame.transform.scale(self.track_selection_default_image,(constants.WIDTH, constants.HEIGHT))
        self.track_selection_hover_1_image: pygame.Surface = pygame.image.load(constants.TRACK_SELECTION_IMAGE_PATH.format(image_name="1")).convert()
        self.track_selection_hover_1_image = pygame.transform.scale(self.track_selection_hover_1_image,(constants.WIDTH, constants.HEIGHT))
        self.track_selection_hover_2_image: pygame.Surface = pygame.image.load(constants.TRACK_SELECTION_IMAGE_PATH.format(image_name="2")).convert()
        self.track_selection_hover_2_image = pygame.transform.scale(self.track_selection_hover_2_image,(constants.WIDTH, constants.HEIGHT))
        self.track_selection_hover_3_image: pygame.Surface = pygame.image.load(constants.TRACK_SELECTION_IMAGE_PATH.format(image_name="3")).convert()
        self.track_selection_hover_3_image = pygame.transform.scale(self.track_selection_hover_3_image,(constants.WIDTH, constants.HEIGHT))
        self.current_image: pygame.Surface = self.track_selection_default_image

        # Track button rects
        button_width: int = 380
        button_height: int = 213
        self.button_rect_1: pygame.Rect = pygame.Rect(302, 160, button_width, button_height)
        self.button_rect_2: pygame.Rect = pygame.Rect(727, 160, button_width, button_height)
        self.button_rect_3: pygame.Rect = pygame.Rect(302, 420, button_width, button_height)

        # Exit Button
        self.button_font: pygame.font.Font = pygame.font.Font(constants.TEXT_FONT_PATH, 40)
        self.exit_button_rect: pygame.Rect = pygame.Rect(20, constants.HEIGHT - 70, 150, 50)

        self.last_hovered: int = 0

        self.hover_sound: pygame.mixer.Sound = pygame.mixer.Sound(constants.HOVER_SOUND_PATH)
        self.hover_sound.set_volume(0.1)
        self.hover_sound_played: bool = False

    def handle_events(self, events, mouse_pos: tuple[int, int]) -> str:
        """Handles events like button presses"""

        hovered_index: int

        if self.button_rect_1.collidepoint(mouse_pos):
            hovered_index = 1
        elif self.button_rect_2.collidepoint(mouse_pos):
            hovered_index = 2
        elif self.button_rect_3.collidepoint(mouse_pos):
            hovered_index = 3
        elif self.exit_button_rect.collidepoint(mouse_pos):
            hovered_index = 4
        else:
            hovered_index = 0

        if hovered_index != self.last_hovered:
            self.last_hovered = hovered_index

            if hovered_index == 1:
                self.hover_sound.play()
                self.current_image = self.track_selection_hover_1_image
            elif hovered_index == 2:
                self.hover_sound.play()
                self.current_image = self.track_selection_hover_2_image
            elif hovered_index == 3:
                self.hover_sound.play()
                self.current_image = self.track_selection_hover_3_image
            elif hovered_index == 4:
                self.hover_sound.play()
                self.current_image = self.track_selection_default_image
            else:
                self.current_image = self.track_selection_default_image

        for event in events:
            if event.type == pygame.QUIT:
                return "exit"
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if hovered_index == 1:
                    return constants.TRACK_NAMES[0]
                elif hovered_index == 2:
                    return constants.TRACK_NAMES[1]
                elif hovered_index == 3:
                    return constants.TRACK_NAMES[2]
                elif hovered_index == 4:
                    return "exit"

        return ""

    def draw(self) -> None:
        """Draws the track selection screen"""
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