import pygame

import constants


class TitleScreen:
    """Handles the title screen."""

    def __init__(self, screen):
        self.screen = screen
        self.title_image: pygame.Surface = pygame.image.load(f"{constants.TITLE_IMAGE_PATH}{constants.TITLE_IMAGE_WITH_BUTTON_EXTENSION}").convert()
        self.title_image = pygame.transform.scale(self.title_image, (constants.WIDTH, constants.HEIGHT))
        button_width, button_height = 425, 200
        button_x = (constants.WIDTH - button_width) / 2
        button_y = constants.HEIGHT - 405
        self.button_rect = pygame.Rect(button_x, button_y, button_width, button_height)

    def handle_events(self, events):
        mouse_pos = pygame.mouse.get_pos()
        if self.button_rect.collidepoint(mouse_pos):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.button_rect.collidepoint(mouse_pos):
                    return "start_game"
        return None

    def draw(self):
        self.screen.blit(self.title_image, (0, 0))
        pygame.display.flip()