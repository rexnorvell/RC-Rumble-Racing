import pygame

import constants


class TrackSelection:
    """Handles the track selection screen."""

    def __init__(self, screen) -> None:
        self.screen: pygame.Surface = screen

        self.track_selection_default_image: pygame.Surface = pygame.image.load(f"{constants.TRACK_SELECTION_IMAGE_PATH}{constants.TRACK_SELECTION_DEFAULT_EXTENSION}").convert()
        self.track_selection_default_image = pygame.transform.scale(self.track_selection_default_image, (constants.WIDTH, constants.HEIGHT))
        self.track_selection_hover_1_image: pygame.Surface = pygame.image.load(f"{constants.TRACK_SELECTION_IMAGE_PATH}1{constants.TRACK_SELECTION_HOVER_EXTENSION}").convert()
        self.track_selection_hover_1_image = pygame.transform.scale(self.track_selection_hover_1_image,(constants.WIDTH, constants.HEIGHT))
        self.track_selection_hover_2_image: pygame.Surface = pygame.image.load(f"{constants.TRACK_SELECTION_IMAGE_PATH}2{constants.TRACK_SELECTION_HOVER_EXTENSION}").convert()
        self.track_selection_hover_2_image = pygame.transform.scale(self.track_selection_hover_2_image,(constants.WIDTH, constants.HEIGHT))
        self.track_selection_hover_3_image: pygame.Surface = pygame.image.load(f"{constants.TRACK_SELECTION_IMAGE_PATH}3{constants.TRACK_SELECTION_HOVER_EXTENSION}").convert()
        self.track_selection_hover_3_image = pygame.transform.scale(self.track_selection_hover_3_image,(constants.WIDTH, constants.HEIGHT))
        self.current_image: pygame.Surface = self.track_selection_default_image

        button_width: int = 435
        button_height: int = 250
        self.button_rect_1: pygame.Rect = pygame.Rect(65, 137, button_width, button_height)
        self.button_rect_2: pygame.Rect = pygame.Rect(909, 137, button_width, button_height)
        self.button_rect_3: pygame.Rect = pygame.Rect(487, 408, button_width, button_height)

        self.last_hovered: int = 0

    def handle_events(self, events) -> str:
        """Handles events like button presses and cursor updates."""
        mouse_pos: tuple[int, int] = pygame.mouse.get_pos()

        if self.button_rect_1.collidepoint(mouse_pos):
            hovered_index = 1
        elif self.button_rect_2.collidepoint(mouse_pos):
            hovered_index = 2
        elif self.button_rect_3.collidepoint(mouse_pos):
            hovered_index = 3
        else:
            hovered_index = 0

        if hovered_index != self.last_hovered:
            self.last_hovered = hovered_index

            if hovered_index == 1:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                self.current_image = self.track_selection_hover_1_image
            elif hovered_index == 2:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                self.current_image = self.track_selection_hover_2_image
            elif hovered_index == 3:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                self.current_image = self.track_selection_hover_3_image
            else:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                self.current_image = self.track_selection_default_image

        for event in events:
            if event.type == pygame.QUIT:
                return "exit"
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                pygame.mouse.set_visible(False)
                if hovered_index == 1:
                    return constants.TRACK_NAMES[0]
                elif hovered_index == 2:
                    return constants.TRACK_NAMES[1]
                elif hovered_index == 3:
                    return constants.TRACK_NAMES[2]

        return ""

    def draw(self) -> None:
        """Draws the track selection screen."""
        self.screen.blit(self.current_image, (0, 0))