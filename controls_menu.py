import pygame
import constants
from ui_elements import ConfirmationDialog


class ControlsMenu:
    """Screen for re-binding controls."""

    def __init__(self, screen: pygame.Surface, save_manager) -> None:
        self.screen = screen
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
        self.label_font = pygame.font.Font(constants.TEXT_FONT_PATH, 50)
        self.key_font = pygame.font.Font(constants.FALLBACK_FONT_PATH, 40)
        self.button_font = pygame.font.Font(constants.TEXT_FONT_PATH, 40)

        self.current_bindings = self.save_manager.get_key_bindings().copy()
        self.initial_bindings = self.save_manager.get_key_bindings().copy()

        # Bindings to display
        self.binding_order = [
            (constants.KEY_ACTION_FORWARD, "Forward"),
            (constants.KEY_ACTION_BACKWARD, "Backward"),
            (constants.KEY_ACTION_LEFT, "Left"),
            (constants.KEY_ACTION_RIGHT, "Right"),
            (constants.KEY_ACTION_DRIFT, "Drift"),
            (constants.KEY_ACTION_TOGGLE_GHOST, "Toggle Ghost"),
        ]

        self.binding_rects: dict[str, pygame.Rect] = {}
        self.generate_rects()

        # Buttons
        self.back_button_rect = pygame.Rect(20, constants.HEIGHT - 70, 150, 50)
        self.save_button_rect = pygame.Rect(constants.WIDTH - 170, constants.HEIGHT - 70, 150, 50)

        self.last_hovered = "none"  # "back", "save", or action_key
        self.awaiting_input_for = None  # Stores the action_key (e.g., "FORWARD")
        self.dialog = None
        self.hover_sound = pygame.mixer.Sound(constants.HOVER_SOUND_PATH)
        self.hover_sound.set_volume(self.save_manager.get_volumes()["sfx"])

    def generate_rects(self):
        """Creates the rects for the key binding buttons."""
        start_x = constants.WIDTH // 2 + 100
        start_y = 200
        gap = 80
        btn_width = 300
        btn_height = 60

        for i, (action_key, label_text) in enumerate(self.binding_order):
            y = start_y + i * gap
            rect = pygame.Rect(start_x, y, btn_width, btn_height)
            self.binding_rects[action_key] = rect

    def settings_changed(self) -> bool:
        """Checks if settings are different from initial."""
        return self.current_bindings != self.initial_bindings

    def handle_events(self, events, mouse_pos: tuple[int, int]) -> str:
        """Returns 'back', 'exit', or ''."""

        if self.dialog:
            action = self.dialog.handle_events(events, mouse_pos)
            if action == "yes":
                self.save_manager.update_key_bindings(self.current_bindings)
                self.save_manager.save_data()
                self.initial_bindings = self.current_bindings.copy()
                self.dialog = None
            elif action == "no":
                self.dialog = None
            return ""

        if self.awaiting_input_for:
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key != pygame.K_ESCAPE:  # Not allowed
                        # Check if key is already used
                        for action, key in self.current_bindings.items():
                            if key == event.key and action != self.awaiting_input_for:
                                self.current_bindings[action] = -1  # Unbind old one (set to invalid)

                        self.current_bindings[self.awaiting_input_for] = event.key
                        self.awaiting_input_for = None
                    elif event.key == pygame.K_ESCAPE:
                        self.awaiting_input_for = None  # Cancel binding
            return ""

        hovered = "none"
        if self.back_button_rect.collidepoint(mouse_pos):
            hovered = "back"
        elif self.settings_changed() and self.save_button_rect.collidepoint(mouse_pos):
            hovered = "save"
        else:
            for action_key, rect in self.binding_rects.items():
                if rect.collidepoint(mouse_pos):
                    hovered = action_key
                    break

        if hovered != self.last_hovered and hovered != "none":
            self.hover_sound.play()
        self.last_hovered = hovered

        for event in events:
            if event.type == pygame.QUIT:
                return "exit"

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if hovered == "back":
                    # Discard changes
                    self.current_bindings = self.initial_bindings.copy()
                    return "back"
                elif hovered == "save":
                    self.save_manager.game.click_sound.play()
                    self.dialog = ConfirmationDialog(self.screen, "Save changes?", self.button_font)
                elif hovered in self.binding_rects:
                    self.save_manager.game.click_sound.play()
                    self.awaiting_input_for = hovered
        return ""

    def draw(self) -> None:
        self.screen.blit(self.background, (0, 0))
        self.screen.blit(self.overlay, (0, 0))

        # Title
        title_surf = self.title_font.render("Controls", True, (255, 255, 255))
        title_rect = title_surf.get_rect(center=(constants.WIDTH // 2, 100))
        self.screen.blit(title_surf, title_rect)

        # Draw bindings
        for action_key, label_text in self.binding_order:
            rect = self.binding_rects[action_key]

            # Label
            label_surf = self.label_font.render(label_text, True, (255, 255, 255))
            label_rect = label_surf.get_rect(midright=(rect.left - 30, rect.centery))
            self.screen.blit(label_surf, label_rect)

            # Key button
            key_code = self.current_bindings.get(action_key, -1)
            key_name = "..."
            if self.awaiting_input_for == action_key:
                key_name = "..."
            elif key_code == -1:
                key_name = "UNBOUND"
            else:
                try:
                    key_name = pygame.key.name(key_code).upper()
                except:
                    key_name = "UNKNOWN"

            btn_color = (50, 50, 50)
            if self.last_hovered == action_key or self.awaiting_input_for == action_key:
                btn_color = constants.TEXT_COLOR

            pygame.draw.rect(self.screen, btn_color, rect, border_radius=8)

            key_surf = self.key_font.render(key_name, True, (255, 255, 255))
            key_rect = key_surf.get_rect(center=rect.center)
            self.screen.blit(key_surf, key_rect)

        # Back Button
        back_color = constants.TRACK_SELECTION_EXIT_HOVER_COLOR if self.last_hovered == "back" else constants.TRACK_SELECTION_EXIT_COLOR
        back_surf = self.button_font.render("Back", True, back_color)
        self.screen.blit(back_surf, back_surf.get_rect(center=self.back_button_rect.center))

        # Save Button
        save_color = constants.TRACK_SELECTION_EXIT_COLOR
        if self.settings_changed():
            save_color = (0, 200, 0)  # Green
            if self.last_hovered == "save":
                save_color = (100, 255, 100)  # Light Green

        save_surf = self.button_font.render("Save", True, save_color)
        self.screen.blit(save_surf, save_surf.get_rect(center=self.save_button_rect.center))

        if self.dialog:
            self.dialog.draw()