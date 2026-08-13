import pygame

from ..utilities import constants
from ..utilities import utilities
from ..utilities.ui_elements import ConfirmationDialog
from ..enums.game_state import GameState
from ..types.menu_results import MenuResults


class SaveSelection:
    """Screen for selecting one of three save files."""

    def __init__(self, game, screen: pygame.Surface, save_manager) -> None:

        self.name: str = "save_selection"
        self.game = game
        self.screen: pygame.Surface = screen
        self.save_manager = save_manager

        self.background: pygame.Surface = pygame.image.load(
            constants.GENERAL_IMAGE_PATH.format(name="background")).convert()
        self.background = pygame.transform.scale(self.background, (constants.WIDTH, constants.HEIGHT))
        self.overlay = pygame.Surface((constants.WIDTH, constants.HEIGHT), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 150))

        self.title_font = pygame.font.Font(constants.TEXT_FONT_PATH, 80)
        self.slot_font = pygame.font.Font(constants.TEXT_FONT_PATH, 50)
        self.info_font = pygame.font.Font(constants.FALLBACK_FONT_PATH, 24)
        self.button_font = pygame.font.Font(constants.TEXT_FONT_PATH, 40)

        # STATE
        self.delete_mode: bool = False
        self.dialog: ConfirmationDialog | None = None
        self.pending_delete_slot: int = -1
        self.last_hovered = "none"
        self.summaries: list[dict | None] = []
        self.show_delete_button: bool = False

        self.load_summaries()

        # Slot Rects
        slot_width = 800
        slot_height = 130
        slot_gap = 30
        start_y = 180
        center_x = constants.WIDTH // 2
        slot_x = center_x - (slot_width / 2)
        self.slot_rects: list[pygame.Rect] = []
        for i in range(constants.NUM_SAVE_SLOTS):
            rect = pygame.Rect(slot_x, start_y + i * (slot_height + slot_gap), slot_width, slot_height)
            self.slot_rects.append(rect)

        # Buttons
        self.back_button_rect = pygame.Rect(20, constants.HEIGHT - 70, 150, 50)
        self.delete_button_rect = pygame.Rect(constants.WIDTH - 220, constants.HEIGHT - 70, 200, 50)

        self.hover_sound = pygame.mixer.Sound(constants.HOVER_SOUND_PATH)
        self.hover_sound.set_volume(self.save_manager.get_volumes()["sfx"])

    def load_summaries(self) -> None:
        self.summaries = [self.save_manager.get_save_summary(i) for i in range(constants.NUM_SAVE_SLOTS)]
        self.show_delete_button = any(not s["empty"] for s in self.summaries)

        if self.delete_mode and not self.show_delete_button:
            self.delete_mode = False

    def handle_events(self, events, mouse_pos: tuple[int, int]) -> MenuResults | None:
        if self.dialog:
            action = self.dialog.handle_events(events, mouse_pos)
            if action == "yes":
                self.save_manager.delete_save_data(self.pending_delete_slot)
                self.load_summaries()
                self.dialog = None
                self.pending_delete_slot = -1
            elif action == "no":
                self.dialog = None
                self.pending_delete_slot = -1
            return None

        hovered = "none"
        if self.back_button_rect.collidepoint(mouse_pos):
            hovered = "back"
        elif self.show_delete_button and self.delete_button_rect.collidepoint(mouse_pos):
            hovered = "delete"
        else:
            for i, rect in enumerate(self.slot_rects):
                if rect.collidepoint(mouse_pos):
                    if self.delete_mode and self.summaries[i]["empty"]:
                        continue
                    hovered = f"slot_{i}"
                    break

        if hovered != self.last_hovered and hovered != "none":
            self.hover_sound.play()
        self.last_hovered = hovered

        for event in events:
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if hovered == "back":
                    return MenuResults(next_state=GameState.TITLE_MENU)
                elif hovered == "delete":
                    self.delete_mode = not self.delete_mode
                elif "slot_" in hovered:
                    slot_index = int(hovered.split("_")[1])
                    if self.delete_mode:
                        if not self.summaries[slot_index]["empty"]:
                            self.pending_delete_slot = slot_index
                            self.dialog = ConfirmationDialog(self.screen, "Delete this save file?", self.button_font)
                    else:
                        self.game.set_save_slot_and_load(slot_index)
                        return MenuResults(next_state=GameState.TRACK_SELECTION_MENU)

        return None

    def _draw_content(self, x_offset: int = 0):
        self.screen.blit(self.overlay, (x_offset, 0))

        title_surf = self.title_font.render("Select Save File", True, (255, 255, 255))
        title_rect = title_surf.get_rect(center=(constants.WIDTH // 2 + x_offset, 90))
        self.screen.blit(title_surf, title_rect)

        for i, rect in enumerate(self.slot_rects):
            summary = self.summaries[i]
            hovered = self.last_hovered == f"slot_{i}"
            is_empty = summary["empty"]

            offset_rect = rect.move(x_offset, 0)

            bg_color = (40, 40, 40)
            border_color = constants.TEXT_COLOR

            if self.delete_mode and summary:
                if not is_empty:
                    border_color = (255, 0, 0)
                    if hovered:
                        bg_color = (80, 20, 20)
                else:
                    border_color = (100, 100, 100)
            elif hovered:
                bg_color = (70, 70, 70)

            pygame.draw.rect(self.screen, bg_color, offset_rect, border_radius=10)
            pygame.draw.rect(self.screen, border_color, offset_rect, width=4, border_radius=10)

            # Slot Title
            title_color = (255, 255, 255)
            if self.delete_mode and is_empty:
                title_color = (100, 100, 100)

            slot_title_surf = self.slot_font.render(f"File {i + 1}", True, title_color)
            title_y = offset_rect.centery - (slot_title_surf.get_height() // 2)
            self.screen.blit(slot_title_surf, (offset_rect.x + 40, title_y))

            # --- CENTERED TEXT LOGIC ---
            info_color = (200, 200, 200)
            if self.delete_mode and is_empty:
                info_color = (80, 80, 80)

            # Define the visual center of the "Info" area (Right half of the button)
            # Button width is 800. Center is 400. Info area is 400->800. Center is 600 relative to X.
            info_center_x = offset_rect.x + (offset_rect.width * 0.75)

            if not is_empty:
                unlocked = summary["unlocked_tracks_count"]
                completed = summary["completed_tracks_count"]
                total = summary["total_tracks_count"]

                # Line 1: Tracks Unlocked (Centered)
                line1_text = f"Tracks Unlocked: {unlocked}/{total}"
                line1_surf = self.info_font.render(line1_text, True, info_color)
                line1_rect = line1_surf.get_rect(center=(info_center_x, offset_rect.centery - 15))
                self.screen.blit(line1_surf, line1_rect)

                # Line 2: Tracks Completed (Centered)
                line2_text = f"Tracks Completed: {completed}/{total}"
                line2_surf = self.info_font.render(line2_text, True, info_color)
                line2_rect = line2_surf.get_rect(center=(info_center_x, offset_rect.centery + 15))
                self.screen.blit(line2_surf, line2_rect)
            else:
                # Empty Message (Centered)
                empty_surf = self.info_font.render("[ Empty Slot ]", True, info_color)
                empty_rect = empty_surf.get_rect(center=(info_center_x, offset_rect.centery))
                self.screen.blit(empty_surf, empty_rect)

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
        self._draw_content(0)
        if self.dialog:
            self.dialog.draw()