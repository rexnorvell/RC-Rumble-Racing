import pygame
import constants


class Slider:
    """A simple horizontal slider."""

    def __init__(self, x, y, w, h, min_val, max_val, initial_val):
        self.rect = pygame.Rect(x, y, w, h)
        self.min_val = min_val
        self.max_val = max_val
        self.val = initial_val
        # Make the handle shorter but taller for easier clicking
        self.handle_rect = pygame.Rect(x, y - h, h * 1.5, h * 3)
        self.update_handle_pos()
        self.dragging = False

    def update_handle_pos(self):
        """Updates handle position based on value."""
        percent = (self.val - self.min_val) / (self.max_val - self.min_val)
        self.handle_rect.centerx = self.rect.x + percent * self.rect.width

    def set_val_from_pos(self, x_pos):
        """Updates value based on mouse x position."""
        percent = (x_pos - self.rect.x) / self.rect.width
        percent = max(0, min(1, percent))
        self.val = self.min_val + percent * (self.max_val - self.min_val)
        self.update_handle_pos()

    def handle_event(self, event, mouse_pos):
        """Handles mouse events for dragging. Returns True if value changed."""
        value_changed = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Click on handle or track
            if self.handle_rect.collidepoint(mouse_pos) or (
                    self.rect.inflate(0, 20).collidepoint(mouse_pos) and not self.handle_rect.collidepoint(mouse_pos)):
                self.dragging = True
                self.set_val_from_pos(mouse_pos[0])
                value_changed = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                self.set_val_from_pos(mouse_pos[0])
                value_changed = True
        return value_changed

    def draw(self, surface):
        """Draws the slider."""
        # Draw track
        pygame.draw.rect(surface, (50, 50, 50), self.rect, border_radius=5)
        # Draw handle
        pygame.draw.rect(surface, constants.TEXT_COLOR, self.handle_rect, border_radius=8)


class ConfirmationDialog:
    """A modal dialog for Yes/No confirmation."""

    def __init__(self, screen, text, font):
        self.screen = screen
        self.text = text
        self.font = font

        self.width = 600
        self.height = 300
        self.x = (constants.WIDTH - self.width) // 2
        self.y = (constants.HEIGHT - self.height) // 2
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

        self.text_surf = self.font.render(self.text, True, (255, 255, 255))
        self.text_rect = self.text_surf.get_rect(center=(self.rect.centerx, self.y + 75))

        btn_width = 150
        btn_height = 60
        self.yes_rect = pygame.Rect(self.x + 75, self.y + self.height - 100, btn_width, btn_height)
        self.no_rect = pygame.Rect(self.x + self.width - 75 - btn_width, self.y + self.height - 100, btn_width,
                                   btn_height)

        self.yes_surf = self.font.render("Yes", True, constants.TRACK_SELECTION_EXIT_COLOR)
        self.no_surf = self.font.render("No", True, constants.TRACK_SELECTION_EXIT_COLOR)
        self.yes_hover_surf = self.font.render("Yes", True, constants.TRACK_SELECTION_EXIT_HOVER_COLOR)
        self.no_hover_surf = self.font.render("No", True, constants.TRACK_SELECTION_EXIT_HOVER_COLOR)

        self.hover = "none"  # "yes", "no", "none"

    def handle_events(self, events, mouse_pos):
        """Returns 'yes', 'no', or ''."""
        self.hover = "none"
        if self.yes_rect.collidepoint(mouse_pos):
            self.hover = "yes"
        elif self.no_rect.collidepoint(mouse_pos):
            self.hover = "no"

        for event in events:
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if self.hover == "yes":
                    return "yes"
                if self.hover == "no":
                    return "no"
        return ""

    def draw(self):
        """Draws the dialog."""
        # Dark overlay
        overlay = pygame.Surface((constants.WIDTH, constants.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        # Dialog box
        pygame.draw.rect(self.screen, (20, 20, 20), self.rect, border_radius=15)
        pygame.draw.rect(self.screen, constants.TEXT_COLOR, self.rect, width=4, border_radius=15)

        # Text
        self.screen.blit(self.text_surf, self.text_rect)

        # Buttons
        yes_surf_to_draw = self.yes_hover_surf if self.hover == "yes" else self.yes_surf
        no_surf_to_draw = self.no_hover_surf if self.hover == "no" else self.no_surf
        self.screen.blit(yes_surf_to_draw, yes_surf_to_draw.get_rect(center=self.yes_rect.center))
        self.screen.blit(no_surf_to_draw, no_surf_to_draw.get_rect(center=self.no_rect.center))