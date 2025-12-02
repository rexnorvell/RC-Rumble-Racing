import pygame

import constants
import utilities
from ui_elements import ConfirmationDialog


class SaveSelection:
    """Screen for selecting one of three save files."""

    def __init__(self, game, screen: pygame.Surface, save_manager) -> None:

        # General
        self.name: str = "save_selection"
        self.game = game
        self.screen: pygame.Surface = screen
        self.save_manager = save_manager

        # Background
        self.background: pygame.Surface = pygame.image.load(
            constants.GENERAL_IMAGE_PATH.format(name="background")).convert()
        self.background = pygame.transform.scale(self.background, (constants.WIDTH, constants.HEIGHT))
        self.overlay = pygame.Surface((constants.WIDTH, constants.HEIGHT), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 150))

        # Fonts
        self.title_font = pygame.font.Font(constants.TEXT_FONT_PATH, 80)
        self.slot_font = pygame.font.Font(constants.TEXT_FONT_PATH, 50)
        self.info_font = pygame.font.Font(constants.FALLBACK_FONT_PATH, 30)
        self.button_font = pygame.font.Font(constants.TEXT_FONT_PATH, 40)

        # State
        self.summaries: list[dict | None] = []
        self.load_summaries()
        self.delete_mode: bool = False
        self.dialog: ConfirmationDialog | None = None
        self.pending_delete_slot: int = -1
        self.last_hovered = "none"  # "back", "delete", "slot_0", "slot_1", "slot_2"

        # Slot Rects
        slot_width = 800
        slot_height = 120
        slot_gap = 40
        start_y = 200
        center_x = constants.WIDTH // 2
        slot_x = center_x - (slot_width / 2)
        self.slot_rects: list[pygame.Rect] = []
        for i in range(constants.NUM_SAVE_SLOTS):
            rect = pygame.Rect(slot_x, start_y + i * (slot_height + slot_gap), slot_width, slot_height)
            self.slot_rects.append(rect)

        # Buttons
        self.back_button_rect = pygame.Rect(20, constants.HEIGHT - 70, 150, 50)
        self.delete_button_rect = pygame.Rect(constants.WIDTH - 220, constants.HEIGHT - 70, 200, 50)
        self.show_delete_button: bool = any(s is not None for s in self.summaries)

        # Sounds
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
        self.transition_prev_pause_time: int = 0
        self.transition_next_duration_ms: int = 400
        self.transition_next_pause_time: int = 0

    def load_summaries(self) -> None:
        """Loads summaries for all save slots."""
        self.summaries = [self.save_manager.get_save_summary(i) for i in range(constants.NUM_SAVE_SLOTS)]
        self.show_delete_button = any(s is not None for s in self.summaries)

    def handle_events(self, events, mouse_pos: tuple[int, int]) -> str:
        """Returns 'back', 'exit', or ''."""

        if self.dialog:
            action = self.dialog.handle_events(events, mouse_pos)
            if action == "yes":
                self.save_manager.delete_save_data(self.pending_delete_slot)
                self.load_summaries()  # Refresh summaries
                self.delete_mode = False
                self.dialog = None
                self.pending_delete_slot = -1
            elif action == "no":
                self.dialog = None
                self.pending_delete_slot = -1
            return constants.NO_ACTION_CODE

        if self.transitioning:
            return constants.NO_ACTION_CODE

        hovered = "none"
        if self.back_button_rect.collidepoint(mouse_pos):
            hovered = "back"
        elif self.show_delete_button and self.delete_button_rect.collidepoint(mouse_pos):
            hovered = "delete"
        else:
            for i, rect in enumerate(self.slot_rects):
                if rect.collidepoint(mouse_pos):
                    hovered = f"slot_{i}"
                    break

        if hovered != self.last_hovered and hovered != "none":
            self.hover_sound.play()
        self.last_hovered = hovered

        for event in events:
            if event.type == pygame.QUIT:
                return constants.EXIT_GAME_CODE
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if hovered == "back":
                    return constants.TITLE_SCREEN_NAME
                elif hovered == "delete":
                    self.delete_mode = not self.delete_mode
                elif "slot_" in hovered:
                    slot_index = int(hovered.split("_")[1])
                    if self.delete_mode:
                        # If in delete mode, try to delete
                        if self.summaries[slot_index] is not None:
                            self.pending_delete_slot = slot_index
                            self.dialog = ConfirmationDialog(self.screen, "Delete this save file?", self.button_font)
                    else:
                        # Not in delete mode, load the file
                        self.game.set_save_slot_and_load(slot_index)
                        return constants.TRACK_SELECTION_NAME

        return constants.NO_ACTION_CODE

    def _draw_content(self, x_offset: int = 0):
        """Draws all screen content at the given x_offset."""
        # Blit overlay at offset
        self.screen.blit(self.overlay, (x_offset, 0))

        # Title
        title_surf = self.title_font.render("Select Save File", True, (255, 255, 255))
        title_rect = title_surf.get_rect(center=(constants.WIDTH // 2 + x_offset, 100))
        self.screen.blit(title_surf, title_rect)

        # Draw Slots
        for i, rect in enumerate(self.slot_rects):
            summary = self.summaries[i]
            hovered = self.last_hovered == f"slot_{i}"

            offset_rect = rect.move(x_offset, 0)

            # Determine colors
            bg_color = (40, 40, 40)
            border_color = constants.TEXT_COLOR

            if self.delete_mode and summary:
                border_color = (255, 0, 0)  # Red border in delete mode if file exists
                if hovered:
                    bg_color = (80, 20, 20)
            elif hovered:
                bg_color = (70, 70, 70)

            pygame.draw.rect(self.screen, bg_color, offset_rect, border_radius=10)
            pygame.draw.rect(self.screen, border_color, offset_rect, width=4, border_radius=10)

            # Slot Title
            slot_title_surf = self.slot_font.render(f"File {i + 1}", True, (255, 255, 255))
            self.screen.blit(slot_title_surf, (offset_rect.x + 30, offset_rect.y + 20))

            # Slot Info
            info_text = ""
            if summary:
                count = summary["unlocked_tracks_count"]
                track_word = "Track" if count == 1 else "Tracks"
                info_text = f"{count} {track_word} Unlocked"
            else:
                info_text = "[ Empty Slot ]"

            info_surf = self.info_font.render(info_text, True, (200, 200, 200))
            self.screen.blit(info_surf, (offset_rect.x + 30, offset_rect.y + 75))

        # Back Button
        back_color = constants.TRACK_SELECTION_EXIT_HOVER_COLOR if self.last_hovered == "back" else constants.TRACK_SELECTION_EXIT_COLOR
        back_surf = self.button_font.render("Back", True, back_color)
        offset_back_rect = self.back_button_rect.move(x_offset, 0)
        self.screen.blit(back_surf, back_surf.get_rect(center=offset_back_rect.center))

        # Delete Button
        if self.show_delete_button:
            delete_text = "Cancel Delete" if self.delete_mode else "Delete File"
            del_color = (255, 255, 0) if self.delete_mode else constants.TRACK_SELECTION_EXIT_COLOR
            if self.last_hovered == "delete":
                del_color = (255, 100, 100) if self.delete_mode else constants.TRACK_SELECTION_EXIT_HOVER_COLOR

            del_surf = self.button_font.render(delete_text, True, del_color)
            offset_del_rect = self.delete_button_rect.move(x_offset, 0)
            self.screen.blit(del_surf, del_surf.get_rect(center=offset_del_rect.center))

    def draw(self) -> None:
        self.screen.blit(self.background, (0, 0))

        if self.transitioning:
            self.handle_transitions()
        else:
            self._draw_content(0)  # Draw at base position
            if self.dialog:
                self.dialog.draw()  # Dialog draws on top, no transition

    def handle_transitions(self):
        """Handles screen transitions"""
        current_time: int = pygame.time.get_ticks()
        time_elapsed_ms: int = current_time - self.transition_start_time_ms
        foreground_x: int

        # SLIDE: From Title Screen (Slide in from right)
        if self.transitioning_from_prev:
            if time_elapsed_ms >= self.transition_prev_duration_ms:
                foreground_x = 0
                self.end_transition()
            else:
                transition_time_elapsed_ms: int = min(time_elapsed_ms, self.transition_prev_duration_ms)
                percent_progress: float = transition_time_elapsed_ms / self.transition_prev_duration_ms
                # Slide in from +WIDTH to 0
                foreground_x = constants.WIDTH - int(percent_progress * constants.WIDTH)
            self._draw_content(foreground_x)

        # SLIDE: To Title Screen (Slide out to right)
        elif self.transitioning_to_prev:
            if time_elapsed_ms >= self.transition_prev_duration_ms:
                foreground_x = constants.WIDTH
                self.end_transition()
            else:
                transition_time_elapsed_ms: int = min(time_elapsed_ms, self.transition_prev_duration_ms)
                percent_progress: float = transition_time_elapsed_ms / self.transition_prev_duration_ms
                # Slide out from 0 to +WIDTH
                foreground_x = int(percent_progress * constants.WIDTH)
            self._draw_content(foreground_x)

        # SLIDE: To Track Selection (Slide out to left)
        elif self.transitioning_to_next:
            if time_elapsed_ms >= self.transition_next_duration_ms:
                foreground_x = -constants.WIDTH
                self.end_transition()
            else:
                transition_time_elapsed_ms: int = min(time_elapsed_ms, self.transition_next_duration_ms)
                percent_progress: float = transition_time_elapsed_ms / self.transition_next_duration_ms
                foreground_x = int(-percent_progress * constants.WIDTH)
            self._draw_content(foreground_x)

        # SLIDE: From Track Selection (Slide in from left)
        elif self.transitioning_from_next:
            if time_elapsed_ms >= self.transition_next_duration_ms:
                foreground_x = 0
                self.end_transition()
            else:
                transition_time_elapsed_ms: int = min(time_elapsed_ms, self.transition_next_duration_ms)
                percent_progress: float = transition_time_elapsed_ms / self.transition_next_duration_ms
                # Slide in from -WIDTH to 0
                foreground_x = int(percent_progress * constants.WIDTH) - constants.WIDTH
            self._draw_content(foreground_x)

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
        # Reload summaries when transitioning in, in case they changed
        if self.transitioning_from_prev:
            self.load_summaries()
            self.delete_mode = False