import pygame

import constants
import utilities


class SettingsMenu:
    """Main settings hub screen."""

    def __init__(self, game, screen: pygame.Surface, save_manager) -> None:

        # General
        self.name: str = "settings_menu"
        self.game = game
        self.screen: pygame.Surface = screen
        self.save_manager = save_manager

        # Use the title screen's background
        self.background: pygame.Surface = pygame.image.load(
            constants.GENERAL_IMAGE_PATH.format(name="background")).convert()
        self.background = pygame.transform.scale(self.background, (constants.WIDTH, constants.HEIGHT))

        # Dark overlay
        self.overlay = pygame.Surface((constants.WIDTH, constants.HEIGHT), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 150))

        # Fonts
        self.title_font = pygame.font.Font(constants.TEXT_FONT_PATH, 80)
        self.button_font = pygame.font.Font(constants.TEXT_FONT_PATH, 50)

        # Buttons
        self.buttons = []
        center_x = constants.WIDTH // 2
        start_y = 250
        gap = 100

        self.controls_rect = pygame.Rect(0, 0, 400, 80)
        self.controls_rect.center = (center_x, start_y)

        self.sound_rect = pygame.Rect(0, 0, 400, 80)
        self.sound_rect.center = (center_x, start_y + gap)

        self.back_button_rect = pygame.Rect(20, constants.HEIGHT - 70, 150, 50)

        self.last_hovered = "none"  # "controls", "sound", "back"
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
        """Returns constants.NO_ACTION_CODE or the name of a screen to navigate to"""
        hovered: str = constants.NO_ACTION_CODE

        if self.controls_rect.collidepoint(mouse_pos):
            hovered = constants.CONTROLS_MENU_NAME
        elif self.sound_rect.collidepoint(mouse_pos):
            hovered = constants.SOUND_MENU_NAME
        elif self.back_button_rect.collidepoint(mouse_pos):
            hovered = constants.TITLE_SCREEN_NAME

        if hovered != self.last_hovered and hovered != constants.NO_ACTION_CODE:
            self.hover_sound.play()
        self.last_hovered = hovered

        for event in events:
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if hovered:
                    return hovered
        return constants.NO_ACTION_CODE

    def draw(self) -> None:
        self.screen.blit(self.background, (0, 0))
        self.screen.blit(self.overlay, (0, 0))

        # Title
        title_surf = self.title_font.render("Settings", True, (255, 255, 255))
        title_rect = title_surf.get_rect(center=(constants.WIDTH // 2, 100))
        self.screen.blit(title_surf, title_rect)

        # Controls Button
        controls_color = constants.TRACK_SELECTION_EXIT_HOVER_COLOR if self.last_hovered == constants.CONTROLS_MENU_NAME else constants.TEXT_COLOR
        controls_surf = self.button_font.render("Controls", True, controls_color)
        self.screen.blit(controls_surf, controls_surf.get_rect(center=self.controls_rect.center))

        # Sound Button
        sound_color = constants.TRACK_SELECTION_EXIT_HOVER_COLOR if self.last_hovered == constants.SOUND_MENU_NAME else constants.TEXT_COLOR
        sound_surf = self.button_font.render("Sound", True, sound_color)
        self.screen.blit(sound_surf, sound_surf.get_rect(center=self.sound_rect.center))

        # Back Button
        back_color = constants.TRACK_SELECTION_EXIT_HOVER_COLOR if self.last_hovered == constants.TITLE_SCREEN_NAME else constants.TRACK_SELECTION_EXIT_COLOR
        back_surf = self.button_font.render("Back", True, back_color)
        self.screen.blit(back_surf, back_surf.get_rect(center=self.back_button_rect.center))

        if self.transitioning:
            self.handle_transitions()

    def handle_transitions(self):
        if self.transitioning_to_next or self.transitioning_from_next:
            is_over: bool = utilities.draw_fade_to_black_transition(self.screen, self.transition_start_time_ms,
                                                                    self.transition_next_duration_ms,
                                                                    self.transitioning_to_next,
                                                                    self.transition_next_pause_time,
                                                                    self.game.dark_overlay)
            if is_over:
                self.end_transition()
        elif self.transitioning_from_prev or self.transitioning_to_prev:
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