import pygame

import constants
import utilities


class CarSelection:
    """Handles the car selection screen"""

    def __init__(self, game, screen, save_manager) -> None:

        # General
        self.name: str = "car_selection"
        self.game = game
        self.screen: pygame.Surface = screen
        self.save_manager = save_manager

        # --- Load Background ---
        self.background_image: pygame.Surface = utilities.load_image(constants.CAR_SELECTION_IMAGE_PATH.format(image_name="default"), False, constants.WIDTH, constants.HEIGHT)

        # --- Load Car Sprites ---
        self.car_sprites: dict[str, pygame.Surface] = {}

        # We need to iterate through all cars and their styles to load all possible sprites
        sprite_width = constants.CAR_WIDTH * 5
        sprite_height = constants.CAR_HEIGHT * 5
        for car_def in constants.CAR_DEFINITIONS:
            for style in car_def["styles"]:
                style_name = style["name"]
                if style_name not in self.car_sprites:
                    try:
                        self.car_sprites[style_name] = utilities.load_image(constants.CAR_IMAGE_PATH.format(car_type=style_name), True, sprite_width, sprite_height)
                    except pygame.error as e:
                        print(f"Error loading car sprite {style_name}: {e}")
                        fallback = pygame.Surface((150, 300))
                        fallback.fill(style["color"])
                        self.car_sprites[style_name] = fallback

        # --- Load UI Elements ---
        arrow_width: int = 64
        arrow_height: int = arrow_width
        self.arrow_left_img: pygame.Surface = utilities.load_image(constants.CAR_SELECTION_ARROW_LEFT_PATH, True, arrow_width, arrow_height)
        self.arrow_right_img: pygame.Surface = utilities.load_image(constants.CAR_SELECTION_ARROW_RIGHT_PATH, True, arrow_width, arrow_height)
        self.garage_door: pygame.Surface = utilities.load_image(constants.GENERAL_IMAGE_PATH.format(name="garage"), False, constants.WIDTH, constants.HEIGHT)

        # --- State ---
        self.current_car_index: int = 0
        self.current_style_index: int = 0
        self.last_hovered: str = "none"

        # --- Fonts ---
        self.name_font: pygame.font.Font = pygame.font.Font(constants.TEXT_FONT_PATH, 70)
        self.stats_header_font: pygame.font.Font = pygame.font.Font(constants.TEXT_FONT_PATH, 50)
        self.stats_label_font: pygame.font.Font = pygame.font.Font(constants.FALLBACK_FONT_PATH, 30)
        self.button_font: pygame.font.Font = pygame.font.Font(constants.TEXT_FONT_PATH, 40)

        # --- Define Button Rects ---
        center_x, center_y = constants.WIDTH // 2, constants.HEIGHT // 2
        self.car_display_rect = pygame.Rect(0, 0, 300, 400)
        self.car_display_rect.center = (center_x, center_y - 50)

        self.arrow_left_rect: pygame.Rect = self.arrow_left_img.get_rect(
            centery=self.car_display_rect.centery, right=self.car_display_rect.left - 40
        )
        self.arrow_right_rect: pygame.Rect = self.arrow_right_img.get_rect(
            centery=self.car_display_rect.centery, left=self.car_display_rect.right + 40
        )

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

        # Select Button
        self.select_button_x: int = constants.WIDTH - self.back_button_width - self.back_button_x
        self.select_button_y: int = constants.HEIGHT - self.back_button_height - self.back_button_x
        self.select_default_image: pygame.Surface = utilities.load_image(
            constants.GENERAL_IMAGE_PATH.format(name="arrow_right_default"), True, self.back_button_width,
            self.back_button_height)
        self.select_hover_image: pygame.Surface = utilities.load_image(
            constants.GENERAL_IMAGE_PATH.format(name="arrow_right_hover"), True, self.back_button_width,
            self.back_button_height)
        self.select_button_rect: pygame.Rect = pygame.Rect(self.select_button_x, self.select_button_y, self.back_button_width, self.back_button_height)
        self.select_current_image: pygame.Surface = self.select_default_image

        # Color buttons are now dynamic, stored in a list of (Rect, index)
        self.color_buttons: list[tuple[pygame.Rect, int]] = []

        # --- Sound ---
        self.hover_sound: pygame.mixer.Sound = pygame.mixer.Sound(constants.HOVER_SOUND_PATH)
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

    def _update_color_buttons(self):
        """Recalculates color button positions based on the current car"""
        styles = constants.CAR_DEFINITIONS[self.current_car_index]["styles"]
        self.color_buttons = []

        button_size = 50
        gap = 10
        total_width = (len(styles) * button_size) + ((len(styles) - 1) * gap)
        start_x = (constants.WIDTH // 2) - (total_width / 2)
        y = constants.HEIGHT - 150

        for i in range(len(styles)):
            x = start_x + i * (button_size + gap)
            rect = pygame.Rect(x, y, button_size, button_size)
            self.color_buttons.append((rect, i))

    def handle_events(self, events, mouse_pos: tuple[int, int]) -> str | dict:
        """
        Returns 'exit', 'back', '', or a dict {'car_index': int, 'style_index': int} on select.
        """

        if self.transitioning:
            return constants.NO_ACTION_CODE

        self._update_color_buttons()  # Ensure buttons are up to date

        hovered_key: str = "none"
        hovered_style_index = -1

        # Only interact with left arrow if we are NOT at the first car
        if self.current_car_index > 0 and self.arrow_left_rect.collidepoint(mouse_pos):
            hovered_key = "arrow_left"
        # Only interact with right arrow if we are NOT at the last car
        elif self.current_car_index < len(constants.CAR_DEFINITIONS) - 1 and self.arrow_right_rect.collidepoint(
                mouse_pos):
            hovered_key = "arrow_right"
        elif self.back_button_rect.collidepoint(mouse_pos):
            hovered_key = "back"
        elif self.select_button_rect.collidepoint(mouse_pos):
            hovered_key = "select"
        else:
            for rect, idx in self.color_buttons:
                if rect.collidepoint(mouse_pos):
                    hovered_key = "color_button"
                    hovered_style_index = idx
                    break

        if hovered_key != self.last_hovered and hovered_key != "none":
            self.hover_sound.play()
        self.last_hovered = hovered_key

        for event in events:
            if event.type == pygame.QUIT:
                return constants.EXIT_GAME_CODE

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if hovered_key == "arrow_left":
                    self.current_car_index -= 1
                    self.current_style_index = 0
                elif hovered_key == "arrow_right":
                    self.current_car_index += 1
                    self.current_style_index = 0
                elif hovered_key == "color_button":
                    self.current_style_index = hovered_style_index
                elif hovered_key == "back":
                    return constants.TRACK_SELECTION_NAME
                elif hovered_key == "select":
                    self.game.set_car_style(self.current_car_index, self.current_style_index)
                    return constants.DIFFICULTY_SELECTION_NAME

        return constants.NO_ACTION_CODE

    def _draw_stats(self, car_data: dict) -> None:
        stats_x = constants.WIDTH - 400
        stats_y = 250

        header_surf = self.stats_header_font.render("Stats", True, constants.TEXT_COLOR)
        self.screen.blit(header_surf, (stats_x, stats_y))
        stats_y += header_surf.get_height() + 30

        for stat_name, stat_value in car_data["stats"].items():
            label_surf = self.stats_label_font.render(stat_name, True, (255, 255, 255))
            self.screen.blit(label_surf, (stats_x, stats_y))
            stats_y += label_surf.get_height() + 10

            bar_bg_rect = pygame.Rect(stats_x, stats_y, constants.CAR_STAT_BAR_WIDTH, constants.CAR_STAT_BAR_HEIGHT)
            pygame.draw.rect(self.screen, constants.CAR_STAT_BAR_BG_COLOR, bar_bg_rect, border_radius=5)

            fill_width = (stat_value / constants.CAR_STAT_MAX_VALUE) * constants.CAR_STAT_BAR_WIDTH
            bar_fill_rect = pygame.Rect(stats_x, stats_y, fill_width, constants.CAR_STAT_BAR_HEIGHT)
            pygame.draw.rect(self.screen, constants.CAR_STAT_BAR_COLOR, bar_fill_rect, border_radius=5)

            stats_y += bar_bg_rect.height + 25

    def draw(self) -> None:
        self.screen.blit(self.background_image, (0, 0))

        # Ensure dynamic elements are ready
        self._update_color_buttons()

        car_data = constants.CAR_DEFINITIONS[self.current_car_index]
        styles = car_data["styles"]

        if self.current_style_index >= len(styles):
            self.current_style_index = 0

        current_style = styles[self.current_style_index]
        sprite_to_draw = self.car_sprites.get(current_style["name"])

        # Draw Name
        name_surf = self.name_font.render(car_data["name"], True, constants.TEXT_COLOR)
        self.screen.blit(name_surf, (70, 250))

        # Draw Car
        if sprite_to_draw:
            car_draw_rect = sprite_to_draw.get_rect(center=self.car_display_rect.center)
            self.screen.blit(sprite_to_draw, car_draw_rect)

        # Draw Stats
        self._draw_stats(car_data)

        # Draw Arrows (Only if not at ends of list)
        if self.current_car_index > 0:
            self.screen.blit(self.arrow_left_img, self.arrow_left_rect)

        if self.current_car_index < len(constants.CAR_DEFINITIONS) - 1:
            self.screen.blit(self.arrow_right_img, self.arrow_right_rect)

        # Draw Color Buttons
        for rect, idx in self.color_buttons:
            color = styles[idx]["color"]
            pygame.draw.rect(self.screen, color, rect, border_radius=8)
            if idx == self.current_style_index:
                pygame.draw.rect(self.screen, (0, 0, 0), rect, width=4, border_radius=8)

        # Draw Nav Buttons
        self.back_current_image = self.back_hover_image if self.last_hovered == "back" else self.back_default_image
        self.screen.blit(self.back_current_image, (self.back_button_x, self.back_button_y))

        self.select_current_image = self.select_hover_image if self.last_hovered == "select" else self.select_default_image
        self.screen.blit(self.select_current_image, (self.select_button_x, self.select_button_y))

        # Handle transitions
        if self.transitioning:
            self.handle_transitions()

    def handle_transitions(self):
        """Handles the four kinds of transitions:
            - Transitioning from the previous screen to the current screen (self.transitioning_from_prev)
            - Transitioning from the current screen to the next screen (self.transitioning_to_next)
            - Transitioning from the current screen to the previous screen (self.transitioning_to_prev)
            - Transitioning from the next screen to the current screen (self.transitioning_from_next)
        """
        if self.transitioning_from_prev or self.transitioning_to_prev:
            is_over: bool = utilities.draw_garage_transition(self.screen, self.transition_start_time_ms, self.transition_prev_duration_ms, self.transitioning_to_prev, self.transition_prev_pause_time, self.game.garage_door)
            if is_over:
                self.end_transition()
        elif self.transitioning_from_next or self.transitioning_to_next:
            is_over: bool = utilities.draw_garage_transition(self.screen, self.transition_start_time_ms, self.transition_next_duration_ms, self.transitioning_to_next, self.transition_next_pause_time, self.game.garage_door)
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