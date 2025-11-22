import pygame
import constants
from ui_elements import Slider, ConfirmationDialog


class SoundMenu:
    """Screen for adjusting sound volumes."""

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
        self.button_font = pygame.font.Font(constants.TEXT_FONT_PATH, 40)

        self.current_volumes = self.save_manager.get_volumes().copy()
        self.initial_volumes = self.save_manager.get_volumes().copy()

        # Sliders
        slider_w = 500
        slider_h = 10
        center_x = constants.WIDTH // 2
        slider_x = center_x - slider_w // 2

        self.music_slider = Slider(slider_x, 300, slider_w, slider_h, 0.0, 1.0, self.current_volumes["music"])
        self.sfx_slider = Slider(slider_x, 450, slider_w, slider_h, 0.0, 1.0, self.current_volumes["sfx"])

        self.sliders = [self.music_slider, self.sfx_slider]

        # Buttons
        self.back_button_rect = pygame.Rect(20, constants.HEIGHT - 70, 150, 50)
        self.save_button_rect = pygame.Rect(constants.WIDTH - 170, constants.HEIGHT - 70, 150, 50)

        self.last_hovered = "none"  # "back", "save"
        self.hover_sound = pygame.mixer.Sound(constants.HOVER_SOUND_PATH)
        self.hover_sound.set_volume(self.current_volumes["sfx"])  # Use current SFX

        self.dialog = None

    def settings_changed(self) -> bool:
        """Checks if settings are different from initial."""
        return self.current_volumes != self.initial_volumes

    def handle_events(self, events, mouse_pos: tuple[int, int]) -> str:
        """Returns 'back', 'exit', or ''."""

        if self.dialog:
            action = self.dialog.handle_events(events, mouse_pos)
            if action == "yes":
                self.save_manager.update_volumes(self.current_volumes)
                self.save_manager.save_data()
                self.initial_volumes = self.current_volumes.copy()
                self.dialog = None
            elif action == "no":
                self.dialog = None
            return ""

        hovered = "none"
        slider_dragging = any(s.dragging for s in self.sliders)

        if not slider_dragging:
            if self.back_button_rect.collidepoint(mouse_pos):
                hovered = "back"
            elif self.settings_changed() and self.save_button_rect.collidepoint(mouse_pos):
                hovered = "save"

        if hovered != self.last_hovered and hovered != "none":
            self.hover_sound.play()
        self.last_hovered = hovered

        for event in events:
            if event.type == pygame.QUIT:
                return "exit"

            # Pass event to sliders
            music_changed = self.music_slider.handle_event(event, mouse_pos)
            sfx_changed = self.sfx_slider.handle_event(event, mouse_pos)

            # Update current values
            self.current_volumes["music"] = self.music_slider.val
            self.current_volumes["sfx"] = self.sfx_slider.val

            # Apply changes live
            if music_changed:
                pygame.mixer.music.set_volume(self.current_volumes["music"])
            if sfx_changed:
                # Update all sounds
                self.save_manager.apply_volume_settings()
                self.hover_sound.set_volume(self.current_volumes["sfx"])

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if hovered == "back":
                    # If changed, revert to initial settings
                    if self.settings_changed():
                        self.save_manager.update_volumes(self.initial_volumes)
                        self.save_manager.apply_volume_settings()  # Apply the revert
                    return "back"
                elif hovered == "save":
                    self.save_manager.game.click_sound.play()
                    self.dialog = ConfirmationDialog(self.screen, "Save changes?", self.button_font)
        return ""

    def draw(self) -> None:
        self.screen.blit(self.background, (0, 0))
        self.screen.blit(self.overlay, (0, 0))

        # Title
        title_surf = self.title_font.render("Sound", True, (255, 255, 255))
        title_rect = title_surf.get_rect(center=(constants.WIDTH // 2, 100))
        self.screen.blit(title_surf, title_rect)

        # Music Slider
        music_label = self.label_font.render("Music", True, (255, 255, 255))
        self.screen.blit(music_label, (self.music_slider.rect.x, self.music_slider.rect.y - 70))
        music_val_label = self.label_font.render(f"{int(self.music_slider.val * 100)}", True, (255, 255, 255))
        self.screen.blit(music_val_label, (self.music_slider.rect.right + 30, self.music_slider.rect.centery - 25))
        self.music_slider.draw(self.screen)

        # SFX Slider
        sfx_label = self.label_font.render("SFX", True, (255, 255, 255))
        self.screen.blit(sfx_label, (self.sfx_slider.rect.x, self.sfx_slider.rect.y - 70))
        sfx_val_label = self.label_font.render(f"{int(self.sfx_slider.val * 100)}", True, (255, 255, 255))
        self.screen.blit(sfx_val_label, (self.sfx_slider.rect.right + 30, self.sfx_slider.rect.centery - 25))
        self.sfx_slider.draw(self.screen)

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