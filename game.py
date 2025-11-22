import sys
import pygame

import constants
from title_screen import TitleScreen
from track_selection import TrackSelection
from car_selection import CarSelection
from difficulty_selection import DifficultySelection
from save_manager import SaveManager
from race import Race

# --- NEW: Import settings screens ---
from settings_menu import SettingsMenu
from controls_menu import ControlsMenu
from sound_menu import SoundMenu


# --- End New ---


class Game:
    """Manages the overall game state, main loop, and coordination between Car and Track"""

    def __init__(self) -> None:
        pygame.init()
        pygame.font.init()
        pygame.mixer.init()

        self.width = constants.WIDTH
        self.height = constants.HEIGHT
        self.screen: pygame.Surface = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
        self.game_surface: pygame.Surface = pygame.Surface((self.width, self.height))
        self.clock: pygame.time.Clock = pygame.time.Clock()
        pygame.display.set_caption(constants.GAME_TITLE)

        # Data Manager
        self.save_manager = SaveManager(self)

        # Menu screens
        self.title_screen: TitleScreen
        self.track_selection: TrackSelection
        self.car_selection: CarSelection
        self.difficulty_selection: DifficultySelection
        # --- NEW ---
        self.settings_menu: SettingsMenu
        self.controls_menu: ControlsMenu
        self.sound_menu: SoundMenu
        # --- End New ---

        self.custom_cursor_image: pygame.Surface = pygame.image.load(
            constants.GENERAL_IMAGE_PATH.format(name="cursor")).convert_alpha()
        self.custom_cursor_image = pygame.transform.scale(self.custom_cursor_image,
                                                          (constants.CURSOR_WIDTH, constants.CURSOR_HEIGHT))
        self.click_sound: pygame.mixer.Sound = pygame.mixer.Sound(constants.CLICK_SOUND_PATH)
        self.hover_sound: pygame.mixer.Sound = pygame.mixer.Sound(constants.HOVER_SOUND_PATH)

        # Apply volumes from save file
        self.save_manager.apply_all_settings()

        # Letterbox scaling
        self.scale_factor: float = 1.0
        self.offset_x: int = 0
        self.offset_y: int = 0

        # Race
        self.race: Race

    def draw_letterboxed_surface(self) -> None:
        """Calculates letterbox scaling and blits the game_surface to the screen"""

        window_width, window_height = self.screen.get_size()
        if window_width == 0 or window_height == 0:
            return  # Avoid division by zero if window is minimized

        # Calculate aspect ratios
        window_aspect: float = window_width / window_height
        game_aspect: float = constants.WIDTH / constants.HEIGHT

        # Determine scaling factor
        new_width: int = window_width
        new_height: int = window_height
        if window_aspect > game_aspect:
            # Window is wider than game
            self.scale_factor = window_height / constants.HEIGHT
            new_width = int(constants.WIDTH * self.scale_factor)
        else:
            # Window is taller than game
            self.scale_factor = window_width / constants.WIDTH
            new_height = int(constants.HEIGHT * self.scale_factor)

        # Calculate offsets for centering
        self.offset_x: int = (window_width - new_width) // 2
        self.offset_y: int = (window_height - new_height) // 2

        # Scale and blit
        scaled_surface: pygame.Surface = pygame.transform.scale(self.game_surface, (new_width, new_height))
        self.screen.fill((0, 0, 0))
        self.screen.blit(scaled_surface, (self.offset_x, self.offset_y))

    def _set_title_screen(self):
        self.title_screen = TitleScreen(self.game_surface, self.save_manager)

        # --- NEW: Settings Menu Methods ---

    def _settings_menu(self) -> str:
        """Displays the main settings menu. Returns next screen."""
        self.settings_menu = SettingsMenu(self.game_surface, self.save_manager)
        settings_clock = pygame.time.Clock()

        running = True
        while running:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.quit()
                if event.type == pygame.VIDEORESIZE:
                    self.screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)

            self.get_scaled_mouse_pos()
            action = self.settings_menu.handle_events(events, self.scaled_mouse_pos)

            if action == "exit":
                self.quit()
            elif action == "back":
                self.click_sound.play()
                return "title"  # Go back to title
            elif action == "controls":
                self.click_sound.play()
                self._controls_menu()  # Run controls sub-loop
                # After returning, re-init main settings
                self.settings_menu = SettingsMenu(self.game_surface, self.save_manager)
            elif action == "sound":
                self.click_sound.play()
                self._sound_menu()  # Run sound sub-loop
                # After returning, re-init main settings
                self.settings_menu = SettingsMenu(self.game_surface, self.save_manager)

            self.settings_menu.draw()
            self.draw_cursor()
            self.draw_letterboxed_surface()
            pygame.display.flip()
            settings_clock.tick(60)
        return "title"

    def _controls_menu(self) -> None:
        """Displays the controls settings menu."""
        self.controls_menu = ControlsMenu(self.game_surface, self.save_manager)
        controls_clock = pygame.time.Clock()

        running = True
        while running:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.quit()
                if event.type == pygame.VIDEORESIZE:
                    self.screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)

            self.get_scaled_mouse_pos()
            action = self.controls_menu.handle_events(events, self.scaled_mouse_pos)

            if action == "exit":
                self.quit()
            elif action == "back":
                self.click_sound.play()
                running = False  # Exit loop, return to _settings_menu

            self.controls_menu.draw()
            self.draw_cursor()
            self.draw_letterboxed_surface()
            pygame.display.flip()
            controls_clock.tick(60)

    def _sound_menu(self) -> None:
        """Displays the sound settings menu."""
        self.sound_menu = SoundMenu(self.game_surface, self.save_manager)
        sound_clock = pygame.time.Clock()

        running = True
        while running:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.quit()
                if event.type == pygame.VIDEORESIZE:
                    self.screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)

            self.get_scaled_mouse_pos()
            action = self.sound_menu.handle_events(events, self.scaled_mouse_pos)

            if action == "exit":
                self.quit()
            elif action == "back":
                self.click_sound.play()
                running = False  # Exit loop, return to _settings_menu

            self.sound_menu.draw()
            self.draw_cursor()
            self.draw_letterboxed_surface()
            pygame.display.flip()
            sound_clock.tick(60)

    # --- End New ---

    def welcome(self) -> None:
        """Displays the title screen and manages main screen transitions"""

        pygame.mouse.set_visible(False)
        pygame.mixer.music.load(constants.GENERAL_AUDIO_PATH.format(song_name="intro"))
        pygame.mixer.music.set_volume(self.save_manager.get_volumes()["music"])
        pygame.mixer.music.play(-1)
        self._set_title_screen()
        title_clock: pygame.time.Clock = pygame.time.Clock()
        if not self.title_screen.play_intro(self.screen):
            self.quit()
        pygame.mouse.set_visible(False)

        current_screen = "title"

        running: bool = True
        queued_action: str = ""
        while running:
            # --- Music Loop ---
            if not pygame.mixer.music.get_busy():
                pygame.mixer.music.load(constants.GENERAL_AUDIO_PATH.format(song_name="intro"))
                pygame.mixer.music.set_volume(self.save_manager.get_volumes()["music"])
                pygame.mixer.music.play(-1)

            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.quit()
                if event.type == pygame.VIDEORESIZE:
                    self.screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)

            self.get_scaled_mouse_pos()

            # --- NEW: State Machine ---
            if current_screen == "title":
                next_action = self.title_screen.handle_events(events, self.scaled_mouse_pos)

                if next_action == "exit":
                    self.quit()
                elif next_action == "track_selection":
                    self.click_sound.play()
                    queued_action = "track_selection"
                    self.title_screen.initialize_transition(start_transition=True, backwards=False)
                elif next_action == "settings":
                    self.click_sound.play()
                    current_screen = self._settings_menu()  # This loop will run until it returns
                    self._set_title_screen()  # Re-init title screen when returning

            if queued_action != "" and not self.title_screen.transitioning:
                should_transition: bool = self._track_select()
                queued_action = ""
                if should_transition:
                    self.title_screen.initialize_transition(start_transition=False, backwards=True)
            self.title_screen.draw()
            self.draw_cursor()
            self.draw_letterboxed_surface()
            pygame.display.flip()
            title_clock.tick(60)

    def get_scaled_mouse_pos(self) -> None:
        """Scales mouse position from window coordinates to game_surface coordinates"""
        pos = pygame.mouse.get_pos()
        if self.scale_factor == 0:  # Prevent divide-by-zero
            self._set_scaled_mouse_pos(x=0, y=0)
        else:
            # Un-scale and un-offset the mouse position
            game_x = (pos[0] - self.offset_x) / self.scale_factor
            game_y = (pos[1] - self.offset_y) / self.scale_factor
            self._set_scaled_mouse_pos(int(game_x), int(game_y))

    def _set_scaled_mouse_pos(self, x: int, y: int) -> None:
        self.scaled_mouse_pos = (x, y)

    def draw_cursor(self) -> None:
        """Draws the custom cursor on the game surface"""
        if self.scaled_mouse_pos[0] not in [0, constants.WIDTH - 1] and self.scaled_mouse_pos[1] not in [0,
                                                                                                         constants.HEIGHT - 1]:
            self.game_surface.blit(self.custom_cursor_image, self.scaled_mouse_pos)

    def _track_select(self) -> bool:
        """Displays the track selection screen and starts the game once a track is selected"""
        # Pass save_manager to track selection so it knows what is unlocked
        self.track_selection: TrackSelection = TrackSelection(self.game_surface, self.save_manager)
        self.track_selection.initialize_transition(start_transition=False, backwards=False)
        track_select_clock: pygame.time.Clock = pygame.time.Clock()

        running: bool = True
        queued_action: str = ""
        should_transition_1: bool = False
        while running:
            # Music is handled by welcome()
            events: list[pygame.event.Event] = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.quit()
                if event.type == pygame.VIDEORESIZE:
                    self.screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)

            self.get_scaled_mouse_pos()

            next_action: str = self.track_selection.handle_events(events, self.scaled_mouse_pos)

            if next_action == "back":
                self.click_sound.play()
                self.track_selection.initialize_transition(start_transition=True, backwards=True)
                queued_action = next_action
            elif next_action != "":
                self.click_sound.play()
                queued_action = next_action
                self.track_selection.initialize_transition(start_transition=True, backwards=False)

            if queued_action != "" and queued_action != "back" and not self.track_selection.transitioning:
                should_transition_2: bool = self._car_select(queued_action)
                queued_action = ""
                # Re-initialize track selection to update locks in case a new track was unlocked
                self.track_selection = TrackSelection(self.game_surface, self.save_manager)
                if should_transition_2:
                    self.track_selection.initialize_transition(start_transition=False, backwards=True)
            elif queued_action == "back" and not self.track_selection.transitioning:
                should_transition_1 = True
                break

            self.track_selection.draw()
            self.draw_cursor()
            self.draw_letterboxed_surface()
            pygame.display.flip()
            track_select_clock.tick(60)
        return should_transition_1

    def _car_select(self, track_name: str) -> bool:
        """Displays the car selection screen"""
        self.car_selection = CarSelection(self.game_surface, self.save_manager)
        self.car_selection.initialize_transition(True)
        car_select_clock: pygame.time.Clock = pygame.time.Clock()

        running: bool = True
        exiting: bool = False
        should_transition: bool = True
        while running:
            # Music handled by welcome()
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.quit()
                if event.type == pygame.VIDEORESIZE:
                    self.screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)

            self.get_scaled_mouse_pos()

            # next_action can be "exit", "back", "", or dict with selection info
            next_action = self.car_selection.handle_events(events, self.scaled_mouse_pos)

            if next_action == "exit":
                self.quit()
            elif next_action == "back":
                self.click_sound.play()
                self.car_selection.initialize_transition(False)
                exiting = True
            elif isinstance(next_action, dict):
                # Car was selected
                self.click_sound.play()
                car_index = next_action["car_index"]
                style_index = next_action["style_index"]

                # Go to Difficulty Selection
                difficulty = self._difficulty_select()

                if difficulty == "back":
                    pass  # Loop continues, user is back at car select
                elif difficulty == "exit":
                    self.quit()
                else:
                    # Start the race with the chosen difficulty
                    self._start_race(track_name, car_index, style_index, difficulty)
                    should_transition = False
                    break  # Stop the loop immediately so we don't draw car selection one last time

            if exiting and not self.car_selection.transitioning:
                should_transition = True
                break

            self.car_selection.draw()
            self.draw_cursor()
            self.draw_letterboxed_surface()
            pygame.display.flip()
            car_select_clock.tick(60)
        return should_transition

    def _difficulty_select(self) -> str:
        """Displays the difficulty selection screen. Returns difficulty key, 'back', or 'exit'."""
        self.difficulty_selection = DifficultySelection(self.game_surface, self.save_manager)
        difficulty_clock = pygame.time.Clock()

        running = True
        while running:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    return "exit"
                if event.type == pygame.VIDEORESIZE:
                    self.screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)

            self.get_scaled_mouse_pos()

            action = self.difficulty_selection.handle_events(events, self.scaled_mouse_pos)

            if action:
                if action != "back":
                    self.click_sound.play()
                return action

            self.difficulty_selection.draw()
            self.draw_cursor()
            self.draw_letterboxed_surface()
            pygame.display.flip()
            difficulty_clock.tick(60)

        return "back"

    def _start_race(self, track_name: str, car_index: int, style_index: int, difficulty: str) -> None:
        """Starts the race loop"""
        racing: bool = True
        while racing:
            self.race = Race(self, track_name, car_index, style_index, difficulty, self.save_manager)
            racing = self.race.start()

    def quit(self) -> None:
        """Quits the game"""
        pygame.quit()
        sys.exit()