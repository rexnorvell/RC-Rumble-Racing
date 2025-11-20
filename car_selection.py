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
        # Load all available car sprites into a dictionary for easy lookup
        # This will automatically load the new green/orange sprites
        self.car_sprites: dict[str, pygame.Surface] = {}
        for car_type_name in constants.CAR_TYPES:
            try:
                sprite = pygame.image.load(constants.CAR_IMAGE_PATH.format(car_type=car_type_name)).convert_alpha()
                # Scale sprites for the selection screen (e.g., 5x original size)
                sprite_width = constants.CAR_WIDTH * 5
                sprite_height = constants.CAR_HEIGHT * 5
                self.car_sprites[car_type_name] = pygame.transform.scale(sprite, (sprite_width, sprite_height))
            except pygame.error as e:
                print(f"Error loading car sprite {car_type_name}: {e}")
                # Create fallback sprite
                fallback_sprite = pygame.Surface((150, 300))
                if "red" in car_type_name:
                    fallback_sprite.fill((255, 0, 0))
                elif "blue" in car_type_name:
                    fallback_sprite.fill((0, 0, 255))
                elif "green" in car_type_name:
                    fallback_sprite.fill((0, 255, 0))
                elif "orange" in car_type_name:
                    fallback_sprite.fill((255, 165, 0))
                self.car_sprites[car_type_name] = fallback_sprite

        # --- Load UI Elements ---
        try:
            self.arrow_left_img = pygame.image.load(constants.CAR_SELECTION_ARROW_LEFT_PATH).convert_alpha()
            self.arrow_right_img = pygame.image.load(constants.CAR_SELECTION_ARROW_RIGHT_PATH).convert_alpha()
            self.arrow_left_img = pygame.transform.scale(self.arrow_left_img, (64, 64))
            self.arrow_right_img = pygame.transform.scale(self.arrow_right_img, (64, 64))
        except pygame.error as e:
            print(f"Error loading arrow images: {e}")
            self.arrow_left_img = pygame.Surface((64, 64), pygame.SRCALPHA)
            pygame.draw.polygon(self.arrow_left_img, (255, 255, 255), [(60, 4), (4, 32), (60, 60)])
            self.arrow_right_img = pygame.Surface((64, 64), pygame.SRCALPHA)
            pygame.draw.polygon(self.arrow_right_img, (255, 255, 255), [(4, 4), (60, 32), (4, 60)])

        # --- State ---
        self.current_car_index: int = 0
        self.current_style_index: int = 0  # 0=red, 1=blue, 2=green, 3=orange
        self.last_hovered: str = "none"  # Use strings for clarity

        # --- Fonts ---
        self.name_font: pygame.font.Font = pygame.font.Font(constants.TEXT_FONT_PATH, 70)
        self.stats_header_font: pygame.font.Font = pygame.font.Font(constants.TEXT_FONT_PATH, 50)
        self.stats_label_font: pygame.font.Font = pygame.font.Font(constants.FALLBACK_FONT_PATH, 30)
        self.button_font: pygame.font.Font = pygame.font.Font(constants.TEXT_FONT_PATH, 40)

        # --- Define Button Rects ---
        center_x, center_y = constants.WIDTH // 2, constants.HEIGHT // 2

        # Car display rect (for centering the sprite)
        self.car_display_rect = pygame.Rect(0, 0, 300, 400)  # Placeholder, will be set by sprite
        self.car_display_rect.center = (center_x, center_y - 50)

        # Arrow buttons
        self.arrow_left_rect: pygame.Rect = self.arrow_left_img.get_rect(
            centery=self.car_display_rect.centery, right=self.car_display_rect.left - 40
        )
        self.arrow_right_rect: pygame.Rect = self.arrow_right_img.get_rect(
            centery=self.car_display_rect.centery, left=self.car_display_rect.right + 40
        )

        # Color buttons
        color_button_size = 50
        color_button_gap = 10
        color_button_y = constants.HEIGHT - 150
        total_color_width = (4 * color_button_size) + (3 * color_button_gap)
        start_color_x = center_x - (total_color_width / 2)

        self.color_red_rect: pygame.Rect = pygame.Rect(
            start_color_x, color_button_y, color_button_size, color_button_size
        )
        self.color_blue_rect: pygame.Rect = pygame.Rect(
            start_color_x + (color_button_size + color_button_gap), color_button_y, color_button_size, color_button_size
        )
        self.color_green_rect: pygame.Rect = pygame.Rect(
            start_color_x + 2 * (color_button_size + color_button_gap), color_button_y, color_button_size,
            color_button_size
        )
        self.color_orange_rect: pygame.Rect = pygame.Rect(
            start_color_x + 3 * (color_button_size + color_button_gap), color_button_y, color_button_size,
            color_button_size
        )

        # Bottom navigation buttons
        self.back_button_rect: pygame.Rect = pygame.Rect(20, constants.HEIGHT - 70, 150, 50)
        self.select_button_rect: pygame.Rect = pygame.Rect(constants.WIDTH - 170, constants.HEIGHT - 70, 150, 50)

        # --- Sound ---
        self.hover_sound: pygame.mixer.Sound = pygame.mixer.Sound(constants.HOVER_SOUND_PATH)
        self.hover_sound.set_volume(0.1)

    def handle_events(self, events, mouse_pos: tuple[int, int]) -> str | int:
        """
        Handles events like button presses.
        Returns the selected style index (0=red, 1=blue, 2=green, 3=orange),
        'back' if the back button is clicked, or '' for no action.
        """

        hovered_key: str = "none"
        if self.arrow_left_rect.collidepoint(mouse_pos):
            hovered_key = "arrow_left"
        elif self.arrow_right_rect.collidepoint(mouse_pos):
            hovered_key = "arrow_right"
        elif self.color_red_rect.collidepoint(mouse_pos):
            hovered_key = "color_red"
        elif self.color_blue_rect.collidepoint(mouse_pos):
            hovered_key = "color_blue"
        elif self.color_green_rect.collidepoint(mouse_pos):
            hovered_key = "color_green"
        elif self.color_orange_rect.collidepoint(mouse_pos):
            hovered_key = "color_orange"
        elif self.back_button_rect.collidepoint(mouse_pos):
            hovered_key = "back"
        elif self.select_button_rect.collidepoint(mouse_pos):
            hovered_key = "select"

        if hovered_key != self.last_hovered and hovered_key != "none":
            self.hover_sound.play()
        self.last_hovered = hovered_key

        for event in events:
            if event.type == pygame.QUIT:
                return "exit"

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if hovered_key == "arrow_left":
                    # Decrement car index (does nothing if 1 car)
                    self.current_car_index = (self.current_car_index - 1) % len(constants.CAR_DEFINITIONS)
                    self.current_style_index = 0  # Reset style
                elif hovered_key == "arrow_right":
                    # Increment car index (does nothing if 1 car)
                    self.current_car_index = (self.current_car_index + 1) % len(constants.CAR_DEFINITIONS)
                    self.current_style_index = 0  # Reset style
                elif hovered_key == "color_red":
                    self.current_style_index = 0
                elif hovered_key == "color_blue":
                    self.current_style_index = 1
                elif hovered_key == "color_green":
                    self.current_style_index = 2
                elif hovered_key == "color_orange":
                    self.current_style_index = 3
                elif hovered_key == "back":
                    return "back"
                elif hovered_key == "select":
                    # Return the *style index* (0, 1, 2, or 3), which
                    # game.py already understands as the car choice.
                    return self.current_style_index

        return ""

    def _draw_stats(self, car_data: dict) -> None:
        """Helper function to draw the car stats on the right"""
        stats_x = constants.WIDTH - 400
        stats_y = 250

        # Draw Header
        header_surf = self.stats_header_font.render("Stats", True, constants.TEXT_COLOR)
        header_rect = header_surf.get_rect(topleft=(stats_x, stats_y))
        self.screen.blit(header_surf, header_rect)

        stats_y += header_rect.height + 30

        for stat_name, stat_value in car_data["stats"].items():
            # Draw Stat Label
            label_surf = self.stats_label_font.render(stat_name, True, (255, 255, 255))
            label_rect = label_surf.get_rect(topleft=(stats_x, stats_y))
            self.screen.blit(label_surf, label_rect)

            stats_y += label_rect.height + 10

            # Draw Stat Bar Background
            bar_bg_rect = pygame.Rect(stats_x, stats_y, constants.CAR_STAT_BAR_WIDTH, constants.CAR_STAT_BAR_HEIGHT)
            pygame.draw.rect(self.screen, constants.CAR_STAT_BAR_BG_COLOR, bar_bg_rect, border_radius=5)

            # Draw Stat Bar Foreground
            fill_width = (stat_value / constants.CAR_STAT_MAX_VALUE) * constants.CAR_STAT_BAR_WIDTH
            bar_fill_rect = pygame.Rect(stats_x, stats_y, fill_width, constants.CAR_STAT_BAR_HEIGHT)
            pygame.draw.rect(self.screen, constants.CAR_STAT_BAR_COLOR, bar_fill_rect, border_radius=5)

            stats_y += bar_bg_rect.height + 25

    def draw(self) -> None:
        """Draws the car selection screen"""
        # Draw the background
        self.screen.blit(self.background_image, (0, 0))

        # Get current car data
        car_data = constants.CAR_DEFINITIONS[self.current_car_index]

        # Get current style and sprite
        # Ensure style index is valid for the current car
        if self.current_style_index >= len(car_data["styles"]):
            self.current_style_index = 0

        current_style = car_data["styles"][self.current_style_index]
        style_name = current_style["name"]  # e.g., "f1_car_red"

        # Get the pre-loaded sprite
        sprite_to_draw = self.car_sprites.get(style_name)

        # Draw Car Name (Left)
        name_surf = self.name_font.render(car_data["name"], True, constants.TEXT_COLOR)
        name_rect = name_surf.get_rect(topleft=(70, 250))
        self.screen.blit(name_surf, name_rect)

        # Draw Car Sprite (Center)
        if sprite_to_draw:
            # Center the sprite in the display area
            car_draw_rect = sprite_to_draw.get_rect(center=self.car_display_rect.center)
            self.screen.blit(sprite_to_draw, car_draw_rect)

        # Draw Stats (Right)
        self._draw_stats(car_data)

        # Draw Arrow Buttons
        self.screen.blit(self.arrow_left_img, self.arrow_left_rect)
        self.screen.blit(self.arrow_right_img, self.arrow_right_rect)

        # Draw Color Buttons (Bottom)
        # Get the style definitions for the current car
        styles = car_data["styles"]

        # Red Button
        pygame.draw.rect(self.screen, styles[0]["color"], self.color_red_rect, border_radius=8)
        # Blue Button
        pygame.draw.rect(self.screen, styles[1]["color"], self.color_blue_rect, border_radius=8)
        # Green Button
        pygame.draw.rect(self.screen, styles[2]["color"], self.color_green_rect, border_radius=8)
        # Orange Button
        pygame.draw.rect(self.screen, styles[3]["color"], self.color_orange_rect, border_radius=8)

        # Add highlight if hovered
        if self.last_hovered == "color_red":
            pygame.draw.rect(self.screen, (255, 255, 255), self.color_red_rect, width=4, border_radius=8)
        elif self.last_hovered == "color_blue":
            pygame.draw.rect(self.screen, (255, 255, 255), self.color_blue_rect, width=4, border_radius=8)
        elif self.last_hovered == "color_green":
            pygame.draw.rect(self.screen, (255, 255, 255), self.color_green_rect, width=4, border_radius=8)
        elif self.last_hovered == "color_orange":
            pygame.draw.rect(self.screen, (255, 255, 255), self.color_orange_rect, width=4, border_radius=8)

        # Draw Navigation Buttons
        # Back Button
        back_color = constants.TRACK_SELECTION_EXIT_HOVER_COLOR if self.last_hovered == "back" else constants.TRACK_SELECTION_EXIT_COLOR
        back_text_surf = self.button_font.render("Back", True, back_color)
        back_text_rect = back_text_surf.get_rect(center=self.back_button_rect.center)
        self.screen.blit(back_text_surf, back_text_rect)

        # Select Button
        select_color = constants.TRACK_SELECTION_EXIT_HOVER_COLOR if self.last_hovered == "select" else constants.TRACK_SELECTION_EXIT_COLOR
        select_text_surf = self.button_font.render("Select", True, select_color)
        select_text_rect = select_text_surf.get_rect(center=self.select_button_rect.center)
        self.screen.blit(select_text_surf, select_text_rect)