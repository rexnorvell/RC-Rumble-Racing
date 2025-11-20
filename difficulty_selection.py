import pygame
import constants


class DifficultySelection:
    """Handles the difficulty selection screen (Ghost opponent selection)."""

    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen

        # Use a generic background or one of the existing ones as fallback
        self.background = pygame.Surface((constants.WIDTH, constants.HEIGHT))
        self.background.fill((30, 30, 30))  # Dark Grey

        # Fonts
        self.title_font = pygame.font.Font(constants.TEXT_FONT_PATH, 80)
        self.button_font = pygame.font.Font(constants.TEXT_FONT_PATH, 50)

        # Options
        self.options = [
            {"key": constants.GHOST_DIFFICULTY_PERSONAL_BEST, "label": "Personal Best"},
            {"key": "easy", "label": "Easy Ghost"},
            {"key": "medium", "label": "Medium Ghost"},
            {"key": "hard", "label": "Hard Ghost"},
        ]

        # Setup Buttons
        self.buttons = []
        center_x = constants.WIDTH // 2
        start_y = 250
        gap = 100

        for i, option in enumerate(self.options):
            text_surf = self.button_font.render(option["label"], True, constants.TEXT_COLOR)
            rect = text_surf.get_rect(center=(center_x, start_y + i * gap))
            self.buttons.append({"rect": rect, "key": option["key"], "label": option["label"]})

        self.back_button_rect = pygame.Rect(20, constants.HEIGHT - 70, 150, 50)

        self.last_hovered = None
        self.hover_sound = pygame.mixer.Sound(constants.HOVER_SOUND_PATH)
        self.hover_sound.set_volume(0.1)

    def handle_events(self, events, mouse_pos: tuple[int, int]) -> str:
        """
        Returns the selected difficulty key string, 'back', 'exit', or empty string.
        """
        hovered = None

        if self.back_button_rect.collidepoint(mouse_pos):
            hovered = "back"
        else:
            for btn in self.buttons:
                if btn["rect"].collidepoint(mouse_pos):
                    hovered = btn["key"]
                    break

        if hovered != self.last_hovered and hovered is not None:
            self.hover_sound.play()
        self.last_hovered = hovered

        for event in events:
            if event.type == pygame.QUIT:
                return "exit"
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if hovered:
                    return hovered

        return ""

    def draw(self) -> None:
        self.screen.blit(self.background, (0, 0))

        # Title
        title_surf = self.title_font.render("Select Opponent", True, (255, 255, 255))
        title_rect = title_surf.get_rect(center=(constants.WIDTH // 2, 100))
        self.screen.blit(title_surf, title_rect)

        # Options
        for btn in self.buttons:
            color = constants.TEXT_COLOR
            if btn["key"] == self.last_hovered:
                color = (255, 255, 0)  # Yellow hover

            text_surf = self.button_font.render(btn["label"], True, color)
            self.screen.blit(text_surf, btn["rect"])

        # Back Button
        back_color = (255, 255, 0) if self.last_hovered == "back" else constants.TRACK_SELECTION_EXIT_COLOR
        back_surf = self.button_font.render("Back", True, back_color)
        self.screen.blit(back_surf, back_surf.get_rect(center=self.back_button_rect.center))