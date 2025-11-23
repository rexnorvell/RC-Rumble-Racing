import pygame

import constants
import utilities


class DifficultySelection:
    """Handles the difficulty selection screen (Ghost opponent selection)."""

    def __init__(self, game, screen: pygame.Surface, save_manager) -> None:

        # General
        self.name: str = "difficulty_selection"
        self.game = game
        self.screen: pygame.Surface = screen
        self.save_manager = save_manager

        # Use a generic background or one of the existing ones as fallback
        self.background = pygame.Surface((constants.WIDTH, constants.HEIGHT))
        self.background.fill((30, 30, 30))  # Dark Grey

        # Fonts
        self.title_font = pygame.font.Font(constants.TEXT_FONT_PATH, 80)
        self.button_font = pygame.font.Font(constants.TEXT_FONT_PATH, 50)

        # Options
        self.options = [
            {"key": constants.GHOST_DIFFICULTY_PERSONAL_BEST, "label": "Personal Best", "index": 1},
            {"key": "easy", "label": "Easy Ghost", "index": 2},
            {"key": "medium", "label": "Medium Ghost", "index": 3},
            {"key": "hard", "label": "Hard Ghost", "index": 4}
        ]

        self.difficulties: list[str] = [constants.GHOST_DIFFICULTY_PERSONAL_BEST,
                                        "easy",
                                        "medium",
                                        "hard"]

        # Setup Buttons
        self.buttons = []
        center_x = constants.WIDTH // 2
        start_y = 250
        gap = 100

        for i, option in enumerate(self.options):
            text_surf = self.button_font.render(option["label"], True, constants.TEXT_COLOR)
            rect = text_surf.get_rect(center=(center_x, start_y + i * gap))
            self.buttons.append({"rect": rect, "key": option["key"], "index": option["index"], "label": option["label"]})

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

        self.last_hovered_index: int = 0
        self.hover_sound = pygame.mixer.Sound(constants.HOVER_SOUND_PATH)
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
        """Returns the selected difficulty key string, 'back', 'exit', or empty string."""

        if self.transitioning:
            return constants.NO_ACTION_CODE

        hovered_index: int = -1

        if self.back_button_rect.collidepoint(mouse_pos):
            hovered_index = 0
        else:
            for btn in self.buttons:
                if btn["rect"].collidepoint(mouse_pos):
                    hovered_index = btn["index"]
                    break

        if hovered_index != self.last_hovered_index and hovered_index != -1:
            self.hover_sound.play()
        self.last_hovered_index = hovered_index

        for event in events:
            if event.type == pygame.QUIT:
                return constants.EXIT_GAME_CODE
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if hovered_index > 0:
                    self.game.set_difficulty(self.difficulties[hovered_index - 1])
                    return constants.RACE_SCREEN_NAME
                elif hovered_index == 0:
                    return constants.CAR_SELECTION_NAME

        return constants.NO_ACTION_CODE

    def draw(self) -> None:
        self.screen.blit(self.background, (0, 0))

        # Title
        title_surf = self.title_font.render("Select Opponent", True, (255, 255, 255))
        title_rect = title_surf.get_rect(center=(constants.WIDTH // 2, 100))
        self.screen.blit(title_surf, title_rect)

        # Options
        for btn in self.buttons:
            color = constants.TEXT_COLOR
            if btn["index"] == self.last_hovered_index:
                color = (255, 255, 0)  # Yellow hover

            text_surf = self.button_font.render(btn["label"], True, color)
            self.screen.blit(text_surf, btn["rect"])

        # Back Button
        self.back_current_image = self.back_hover_image if self.last_hovered_index == 0 else self.back_default_image
        self.screen.blit(self.back_current_image, (self.back_button_x, self.back_button_y))

        if self.transitioning:
            self.handle_transitions()

    def handle_transitions(self):
        """Handles the four kinds of transitions:
            - Transitioning from the previous screen to the current screen (self.transitioning_from_prev)
            - Transitioning from the current screen to the next screen (self.transitioning_to_next)
            - Transitioning from the current screen to the previous screen (self.transitioning_to_prev)
            - Transitioning from the next screen to the current screen (self.transitioning_from_next)
        """

        if self.transitioning_to_prev or self.transitioning_from_prev:
            is_over: bool = utilities.draw_garage_transition(self.screen, self.transition_start_time_ms, self.transition_prev_duration_ms, self.transitioning_to_prev, self.transition_prev_pause_time, self.game.garage_door)
            if is_over:
                self.end_transition()
        elif self.transitioning_to_next or self.transitioning_from_next:
            is_over: bool = utilities.draw_fade_to_black_transition(self.screen, self.transition_start_time_ms, self.transition_next_duration_ms, self.transitioning_to_next, self.transition_next_pause_time, self.game.dark_overlay)
            if is_over:
                self.end_transition()

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