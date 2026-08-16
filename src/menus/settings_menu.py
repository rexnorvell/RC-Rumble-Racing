from __future__ import annotations

import pygame

from utilities import constants
from utilities import utilities
from enums.game_state import GameState
from game_types.menu_results import MenuResults


class SettingsMenu:
    """Main settings hub screen."""

    def __init__(self, sound_manager, screen: pygame.Surface, save_manager) -> None:

        # General
        self.name: str = "settings_menu"
        self.sound_manager = sound_manager
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

        self.last_hovered: GameState | None = None

    def handle_events(self, events, mouse_pos: tuple[int, int]) -> MenuResults | None:
        hovered: GameState | None = None

        if self.controls_rect.collidepoint(mouse_pos):
            hovered = GameState.KEYBINDS_MENU
        elif self.sound_rect.collidepoint(mouse_pos):
            hovered = GameState.SOUND_MENU
        elif self.back_button_rect.collidepoint(mouse_pos):
            hovered = GameState.TITLE_MENU

        if hovered is not None and hovered != self.last_hovered:
            self.sound_manager.play_hover()
        self.last_hovered = hovered

        for event in events:
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if hovered is not None:
                    return MenuResults(next_state=hovered)
        return None

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