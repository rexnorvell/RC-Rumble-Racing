import pygame

import constants


class CarSelection:
    """Handles the car selection screen"""

    def __init__(self, screen) -> None:
        self.screen: pygame.Surface = screen

        # --- Load Background ---
        try:
            self.background_image: pygame.Surface = pygame.image.load(
                constants.CAR_SELECTION_IMAGE_PATH.format(image_name="default")
            ).convert()
        except pygame.error as e:
            print(f"Error loading car selection background: {e}")
            self.background_image = pygame.Surface((constants.WIDTH, constants.HEIGHT))
            self.background_image.fill((20, 20, 20))  # Dark fallback

        self.background_image = pygame.transform.scale(
            self.background_image, (constants.WIDTH, constants.HEIGHT)
        )

        # --- Load Car Sprites ---
        self.car_sprites: dict[str, pygame.Surface] = {}

        # We need to iterate through all cars and their styles to load all possible sprites
        for car_def in constants.CAR_DEFINITIONS:
            for style in car_def["styles"]:
                style_name = style["name"]
                if style_name not in self.car_sprites:
                    try:
                        sprite = pygame.image.load(constants.CAR_IMAGE_PATH.format(car_type=style_name)).convert_alpha()
                        sprite_width = constants.CAR_WIDTH * 5
                        sprite_height = constants.CAR_HEIGHT * 5
                        self.car_sprites[style_name] = pygame.transform.scale(sprite, (sprite_width, sprite_height))
                    except pygame.error as e:
                        print(f"Error loading car sprite {style_name}: {e}")
                        fallback = pygame.Surface((150, 300))
                        fallback.fill(style["color"])
                        self.car_sprites[style_name] = fallback

        # --- Load UI Elements ---
        try:
            self.arrow_left_img = pygame.image.load(constants.CAR_SELECTION_ARROW_LEFT_PATH).convert_alpha()
            self.arrow_right_img = pygame.image.load(constants.CAR_SELECTION_ARROW_RIGHT_PATH).convert_alpha()
            self.arrow_left_img = pygame.transform.scale(self.arrow_left_img, (64, 64))
            self.arrow_right_img = pygame.transform.scale(self.arrow_right_img, (64, 64))
        except pygame.error as e:
            self.arrow_left_img = pygame.Surface((64, 64))
            self.arrow_right_img = pygame.Surface((64, 64))
            self.arrow_left_img.fill((255, 255, 255))
            self.arrow_right_img.fill((255, 255, 255))

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

        self.back_button_rect: pygame.Rect = pygame.Rect(20, constants.HEIGHT - 70, 150, 50)
        self.select_button_rect: pygame.Rect = pygame.Rect(constants.WIDTH - 170, constants.HEIGHT - 70, 150, 50)

        # Color buttons are now dynamic, stored in a list of (Rect, index)
        self.color_buttons: list[tuple[pygame.Rect, int]] = []

        # --- Sound ---
        self.hover_sound: pygame.mixer.Sound = pygame.mixer.Sound(constants.HOVER_SOUND_PATH)
        self.hover_sound.set_volume(0.1)

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
        self._update_color_buttons()  # Ensure buttons are up to date

        hovered_key: str = "none"
        hovered_style_index = -1

        if self.arrow_left_rect.collidepoint(mouse_pos):
            hovered_key = "arrow_left"
        elif self.arrow_right_rect.collidepoint(mouse_pos):
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
                return "exit"

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if hovered_key == "arrow_left":
                    self.current_car_index = (self.current_car_index - 1) % len(constants.CAR_DEFINITIONS)
                    self.current_style_index = 0
                elif hovered_key == "arrow_right":
                    self.current_car_index = (self.current_car_index + 1) % len(constants.CAR_DEFINITIONS)
                    self.current_style_index = 0
                elif hovered_key == "color_button":
                    self.current_style_index = hovered_style_index
                elif hovered_key == "back":
                    return "back"
                elif hovered_key == "select":
                    return {
                        "car_index": self.current_car_index,
                        "style_index": self.current_style_index
                    }

        return ""

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

        # Draw Arrows
        self.screen.blit(self.arrow_left_img, self.arrow_left_rect)
        self.screen.blit(self.arrow_right_img, self.arrow_right_rect)

        # Draw Color Buttons
        for rect, idx in self.color_buttons:
            color = styles[idx]["color"]
            pygame.draw.rect(self.screen, color, rect, border_radius=8)
            if idx == self.current_style_index:
                pygame.draw.rect(self.screen, (255, 255, 255), rect, width=4, border_radius=8)

        # Draw Nav Buttons
        back_color = constants.TRACK_SELECTION_EXIT_HOVER_COLOR if self.last_hovered == "back" else constants.TRACK_SELECTION_EXIT_COLOR
        back_surf = self.button_font.render("Back", True, back_color)
        self.screen.blit(back_surf, back_surf.get_rect(center=self.back_button_rect.center))

        select_color = constants.TRACK_SELECTION_EXIT_HOVER_COLOR if self.last_hovered == "select" else constants.TRACK_SELECTION_EXIT_COLOR
        select_surf = self.button_font.render("Select", True, select_color)
        self.screen.blit(select_surf, select_surf.get_rect(center=self.select_button_rect.center))