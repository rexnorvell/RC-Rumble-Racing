import pygame

import constants


class TrackSelection:
    """Handles the track selection screen."""

    def __init__(self, screen) -> None:
        self.screen: pygame.Surface = screen

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

        button_width: int = 435
        button_height: int = 250
        self.button_rect_1: pygame.Rect = pygame.Rect(65, 137, button_width, button_height)
        self.button_rect_2: pygame.Rect = pygame.Rect(909, 137, button_width, button_height)
        self.button_rect_3: pygame.Rect = pygame.Rect(487, 408, button_width, button_height)

        self.last_hovered: int = 0

        self.hover_sound: pygame.mixer.Sound = pygame.mixer.Sound(constants.HOVER_SOUND_PATH)
        self.hover_sound.set_volume(0.1)
        self.hover_sound_played: bool = False

    def handle_events(self, events, window_size: tuple[int, int]) -> str:
        """Handles events like button presses."""

        # Scale mouse position
        unscaled_mouse_pos = pygame.mouse.get_pos()
        mouse_pos: tuple[int, int]
        if window_size[0] == 0 or window_size[1] == 0:
            mouse_pos = (0, 0)
        else:
            game_surface_size = self.screen.get_size()
            scale_x = game_surface_size[0] / window_size[0]
            scale_y = game_surface_size[1] / window_size[1]
            mouse_pos = (int(unscaled_mouse_pos[0] * scale_x), int(unscaled_mouse_pos[1] * scale_y))

        hovered_index: int

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
                self.hover_sound.play()
                self.current_image = self.track_selection_hover_1_image
            elif hovered_index == 2:
                self.hover_sound.play()
                self.current_image = self.track_selection_hover_2_image
            elif hovered_index == 3:
                self.hover_sound.play()
                self.current_image = self.track_selection_hover_3_image
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

        return ""

    def draw(self) -> None:
        """Draws the track selection screen."""
        self.screen.blit(self.current_image, (0, 0))