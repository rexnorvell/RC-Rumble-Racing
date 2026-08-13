import pygame
from pathlib import Path

from ..utilities import constants
from ..utilities import utilities
from ..enums.difficulty import Difficulty
from ..enums.game_state import GameState
from ..types.menu_results import MenuResults


class DifficultySelection:
    """Handles the difficulty selection screen."""

    def __init__(self, game, screen: pygame.Surface, save_manager) -> None:

        self.name: str = "difficulty_selection"
        self.game = game
        self.screen: pygame.Surface = screen
        self.save_manager = save_manager

        self.background = pygame.Surface((constants.WIDTH, constants.HEIGHT))
        self.background.fill((30, 30, 30))

        self.title_font = pygame.font.Font(constants.TEXT_FONT_PATH, 80)
        self.button_font = pygame.font.Font(constants.TEXT_FONT_PATH, 50)

        self.options = [
            {"key": Difficulty.EASY, "label": "Easy Ghost"},
            {"key": Difficulty.MEDIUM, "label": "Medium Ghost"},
            {"key": Difficulty.HARD, "label": "Hard Ghost"},
            {"key": Difficulty.PB, "label": "Personal Best"}
        ]

        self.buttons = []
        center_x = constants.WIDTH // 2
        start_y = 250
        gap = 100

        for i, option in enumerate(self.options):
            text_surf = self.button_font.render(option["label"], True, constants.TEXT_COLOR)
            rect = text_surf.get_rect(center=(center_x, start_y + i * gap))
            self.buttons.append({"rect": rect, "key": option["key"], "label": option["label"]})

        # Back Button
        self.back_button_x: int = 10
        self.back_button_width: int = 100
        self.back_button_height: int = self.back_button_width
        self.back_button_y: int = constants.HEIGHT - self.back_button_height - self.back_button_x
        self.back_default_image: pygame.Surface = utilities.load_image(
            constants.GENERAL_IMAGE_PATH.format(name="arrow_left_default"), True, self.back_button_width,
            self.back_button_height)
        self.back_hover_image: pygame.Surface = utilities.load_image(
            constants.GENERAL_IMAGE_PATH.format(name="arrow_left_hover"), True, self.back_button_width,
            self.back_button_height)
        self.back_button_rect: pygame.Rect = pygame.Rect(self.back_button_x, self.back_button_y,
                                                         self.back_button_width,
                                                         self.back_button_height)
        self.back_current_image: pygame.Surface = self.back_default_image

        self.last_hovered_index: int = -1
        self.hover_sound = pygame.mixer.Sound(constants.HOVER_SOUND_PATH)
        self.hover_sound.set_volume(self.save_manager.get_volumes()["sfx"])

    def _is_personal_best_available(self) -> bool:
        if not hasattr(self.game, "track_name"):
            return False
        pb_path = Path(constants.PERSONAL_BEST_METADATA_FILE_PATH.format(track_name=self.game.track_name.value))
        return pb_path.exists()

    def handle_events(self, events, mouse_pos: tuple[int, int]) -> MenuResults | None:

        hovered_index: int = -1
        pb_available = self._is_personal_best_available()
        current_track = getattr(self.game, "track_name", constants.TRACK_NAMES[0])

        if self.back_button_rect.collidepoint(mouse_pos):
            hovered_index = 0
        else:
            for i, btn in enumerate(self.buttons):
                if btn["rect"].collidepoint(mouse_pos):
                    key = btn["key"]
                    is_disabled = False

                    if key == constants.GHOST_DIFFICULTY_PERSONAL_BEST:
                        if not pb_available: is_disabled = True
                    else:
                        if not self.save_manager.is_difficulty_unlocked(current_track, key):
                            is_disabled = True

                    if is_disabled:
                        continue

                    hovered_index = i + 1
                    break

        if hovered_index != self.last_hovered_index and hovered_index != -1:
            self.hover_sound.play()
        self.last_hovered_index = hovered_index

        for event in events:
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if hovered_index > 0:
                    selected_btn = self.buttons[hovered_index - 1]
                    difficulty: Difficulty = selected_btn["key"]
                    return MenuResults(next_state=GameState.RACE_MENU, difficulty=difficulty)
                elif hovered_index == 0:
                    return MenuResults(next_state=GameState.VEHICLE_SELECTION_MENU)

        return None

    def draw(self) -> None:
        self.screen.blit(self.background, (0, 0))

        title_surf = self.title_font.render("Select Opponent", True, (255, 255, 255))
        title_rect = title_surf.get_rect(center=(constants.WIDTH // 2, 100))
        self.screen.blit(title_surf, title_rect)

        pb_available = self._is_personal_best_available()
        current_track = getattr(self.game, "track_name", constants.TRACK_NAMES[0])

        for i, btn in enumerate(self.buttons):
            color = constants.TEXT_COLOR
            key = btn["key"]
            is_disabled = False

            if key == Difficulty.PB:
                if not pb_available: is_disabled = True
            else:
                if not self.save_manager.is_difficulty_unlocked(current_track, key):
                    is_disabled = True

            if is_disabled:
                color = constants.BUTTON_DISABLED_COLOR
            elif (i + 1) == self.last_hovered_index:
                color = (255, 255, 0)

            text_surf = self.button_font.render(btn["label"], True, color)
            self.screen.blit(text_surf, btn["rect"])

        self.back_current_image = self.back_hover_image if self.last_hovered_index == 0 else self.back_default_image
        self.screen.blit(self.back_current_image, (self.back_button_x, self.back_button_y))