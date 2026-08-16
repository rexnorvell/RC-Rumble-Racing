from __future__ import annotations

import pygame

from utilities import constants
from utilities import utilities
from enums.game_state import GameState
from enums.track_name import TrackName
from game_types.menu_results import MenuResults


class TrackSelection:
    """Handles the track selection screen"""

    TRACK_SELECTION_IMAGE_PATH: str = "assets/images/track_selection/{number}_{type}.png"

    def __init__(self, sound_manager, screen, save_manager) -> None:

        # General
        self.name: str = "track_selection"
        self.sound_manager = sound_manager
        self.screen: pygame.Surface = screen
        self.save_manager = save_manager
        self.num_unlocked: int = self.save_manager.num_unlocked

        # Background image
        self.background_image: pygame.Surface = pygame.image.load(
            constants.GENERAL_IMAGE_PATH.format(name="background")).convert()
        self.background_image = pygame.transform.scale(self.background_image, (constants.WIDTH, constants.HEIGHT))

        # Track button rects
        button_width: int = 380
        button_height: int = 213

        # First track
        self.first_default_image: pygame.Surface = utilities.load_image(
            self.TRACK_SELECTION_IMAGE_PATH.format(number=1, type="default"), True, button_width, button_height)
        self.first_hover_image: pygame.Surface = utilities.load_image(
            self.TRACK_SELECTION_IMAGE_PATH.format(number=1, type="hover"), True, button_width, button_height)

        # Second track
        self.second_default_image: pygame.Surface = utilities.load_image(
            self.TRACK_SELECTION_IMAGE_PATH.format(number=2, type="default"), True, button_width, button_height)
        self.second_hover_image: pygame.Surface = utilities.load_image(
            self.TRACK_SELECTION_IMAGE_PATH.format(number=2, type="hover"), True, button_width, button_height)
        self.second_locked_image: pygame.Surface = utilities.load_image(
            self.TRACK_SELECTION_IMAGE_PATH.format(number=2, type="locked"), True, button_width, button_height)

        # Third track
        self.third_default_image: pygame.Surface = utilities.load_image(
            self.TRACK_SELECTION_IMAGE_PATH.format(number=3, type="default"), True, button_width, button_height)
        self.third_hover_image: pygame.Surface = utilities.load_image(
            self.TRACK_SELECTION_IMAGE_PATH.format(number=3, type="hover"), True, button_width, button_height)
        self.third_locked_image: pygame.Surface = utilities.load_image(
            self.TRACK_SELECTION_IMAGE_PATH.format(number=3, type="locked"), True, button_width, button_height)

        # Fourth track
        self.fourth_default_image: pygame.Surface = utilities.load_image(
            self.TRACK_SELECTION_IMAGE_PATH.format(number=4, type="default"), True, button_width, button_height)
        self.fourth_hover_image: pygame.Surface = utilities.load_image(
            self.TRACK_SELECTION_IMAGE_PATH.format(number=4, type="hover"), True, button_width, button_height)
        self.fourth_locked_image: pygame.Surface = utilities.load_image(
            self.TRACK_SELECTION_IMAGE_PATH.format(number=4, type="locked"), True, button_width, button_height)

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
        self.back_button_rect: pygame.Rect = pygame.Rect(self.back_button_x, self.back_button_y, self.back_button_width,
                                                         self.back_button_height)
        self.back_current_image: pygame.Surface = self.back_default_image

        self.nothing_hovered_index: int = -1
        self.last_hovered_index: int = self.nothing_hovered_index
        self.back_button_index: int = 4

        # Initialize images
        self.first_image: pygame.Surface = self.first_default_image
        self.second_image: pygame.Surface = self.second_default_image
        self.third_image: pygame.Surface = self.third_default_image
        self.fourth_image: pygame.Surface = self.fourth_default_image
        self.set_current_images(self.nothing_hovered_index)

        # Store buttons with their associated track names
        self.buttons = [
            {
                "rect": pygame.Rect(302, 160, button_width, button_height),
                "track": TrackName.MM,
                "index": 0
            },
            {
                "rect": pygame.Rect(727, 160, button_width, button_height),
                "track": TrackName.DD,
                "index": 1
            },
            {
                "rect": pygame.Rect(302, 420, button_width, button_height),
                "track": TrackName.GG,
                "index": 2
            },
            {
                "rect": pygame.Rect(727, 420, button_width, button_height),
                "track": TrackName.FF,
                "index": 3
            }
        ]

    def handle_events(self, events, mouse_pos: tuple[int, int]) -> MenuResults | None:
        """Handles events like button presses"""

        hovered_index: int = self.nothing_hovered_index

        # Check button hovers
        for _, btn in enumerate(self.buttons):
            if btn["rect"].collidepoint(mouse_pos):
                # Only allow hovering if the track is unlocked
                if self.save_manager.is_track_unlocked(btn["track"]):
                    hovered_index = btn["index"]
                break

        # Check back button
        if hovered_index == self.nothing_hovered_index and self.back_button_rect.collidepoint(mouse_pos):
            hovered_index = self.back_button_index

        if hovered_index != self.last_hovered_index:
            self.last_hovered_index = hovered_index
            if hovered_index > self.nothing_hovered_index:
                self.sound_manager.play_hover()
                self.set_current_images(hovered_index)
            else:
                self.set_current_images(self.nothing_hovered_index)

        for event in events:
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if hovered_index == self.back_button_index:
                    return MenuResults(next_state=GameState.SAVE_FILE_MENU)
                elif hovered_index > self.nothing_hovered_index:
                    track_name: TrackName = self.buttons[hovered_index]["track"]
                    return MenuResults(next_state=GameState.VEHICLE_SELECTION_MENU, track_name=track_name)

        return None

    def set_current_images(self, hovered_index: int) -> None:
        """Sets the styles of the images based on which one is being hovered over"""
        self.first_image = self.first_default_image if hovered_index != 0 else self.first_hover_image
        if self.num_unlocked <= 1:
            self.second_image = self.second_locked_image
        elif hovered_index == 1:
            self.second_image = self.second_hover_image
        else:
            self.second_image = self.second_default_image

        if self.num_unlocked <= 2:
            self.third_image = self.third_locked_image
        elif hovered_index == 2:
            self.third_image = self.third_hover_image
        else:
            self.third_image = self.third_default_image

        if self.num_unlocked <= 3:
            self.fourth_image = self.fourth_locked_image
        elif hovered_index == 3:
            self.fourth_image = self.fourth_hover_image
        else:
            self.fourth_image = self.fourth_default_image

        self.back_current_image = self.back_default_image if hovered_index != self.back_button_index else self.back_hover_image

    def draw(self) -> None:
        """Draws the track selection screen"""
        self.screen.blit(self.background_image, (0, 0))
        self.blit_current_images(0)

    def blit_current_images(self, x: int) -> None:
        """Draws the current images to the screen with an optional x offset"""
        self.screen.blit(self.first_image, (x + 302, 160))
        self.screen.blit(self.second_image, (x + 727, 160))
        self.screen.blit(self.third_image, (x + 302, 420))
        self.screen.blit(self.fourth_image, (x + 727, 420))
        self.screen.blit(self.back_current_image, (x + self.back_button_x, self.back_button_y))