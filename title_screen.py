import pygame

import constants


class TitleScreen:
    """Handles the title screen."""

    def __init__(self, screen) -> None:
        self.screen: pygame.Surface = screen
        self.title_default_image: pygame.Surface = pygame.image.load(f"{constants.TITLE_IMAGE_PATH}{constants.TITLE_IMAGE_DEFAULT_EXTENSION}").convert()
        self.title_default_image = pygame.transform.scale(self.title_default_image, (constants.WIDTH, constants.HEIGHT))
        self.title_hover_image: pygame.Surface = pygame.image.load(f"{constants.TITLE_IMAGE_PATH}{constants.TITLE_IMAGE_HOVER_EXTENSION}").convert()
        self.title_hover_image = pygame.transform.scale(self.title_hover_image, (constants.WIDTH, constants.HEIGHT))
        self.title_click_image: pygame.Surface = pygame.image.load(f"{constants.TITLE_IMAGE_PATH}{constants.TITLE_IMAGE_CLICK_EXTENSION}").convert()
        self.title_click_image = pygame.transform.scale(self.title_click_image, (constants.WIDTH, constants.HEIGHT))
        self.current_image: pygame.Surface = self.title_default_image
        button_width: int = 425
        button_height: int = 200
        button_x: float = (constants.WIDTH - button_width) / 2
        button_y: int = constants.HEIGHT - 405
        self.button_rect: pygame.Rect = pygame.Rect(button_x, button_y, button_width, button_height)

    def handle_events(self, events) -> str:
        """Handles events like button presses."""
        mouse_pos: tuple[int, int] = pygame.mouse.get_pos()
        if self.button_rect.collidepoint(mouse_pos):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            self.current_image = self.title_hover_image
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
            self.current_image = self.title_default_image
        for event in events:
            if event.type == pygame.QUIT:
                return "exit"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.button_rect.collidepoint(mouse_pos):
                    self.current_image = self.title_click_image
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if self.button_rect.collidepoint(mouse_pos):
                    self.current_image = self.title_default_image
                    return "track_selection"
        return ""

    def draw(self) -> None:
        """Draws the title screen."""
        self.screen.blit(self.current_image, (0, 0))
        pygame.display.flip()