import pygame

from ..utilities import constants
from ..menus.car_selection import CarSelection
from ..menus.controls_menu import ControlsMenu
from ..menus.difficulty_selection import DifficultySelection
from ..utilities.save_manager import SaveManager
from ..menus.settings_menu import SettingsMenu
from ..menus.sound_menu import SoundMenu
from ..menus.title_screen import TitleScreen
from ..menus.track_selection import TrackSelection
from ..utilities import utilities
from .race import Race


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

        # Initialize with Index 0 (which SaveManager converts to File 1)
        self.save_manager = SaveManager(0)

        # Import here to avoid circular imports
        from src.menus.save_selection import SaveSelection

        # Menu screens
        self.title_screen: TitleScreen = TitleScreen(self, self.game_surface, self.save_manager)
        self.save_selection: SaveSelection = SaveSelection(self, self.game_surface, self.save_manager)
        self.track_selection: TrackSelection = TrackSelection(self, self.game_surface, self.save_manager)
        self.car_selection: CarSelection = CarSelection(self, self.game_surface, self.save_manager)
        self.difficulty_selection: DifficultySelection = DifficultySelection(self, self.game_surface, self.save_manager)
        self.settings_menu: SettingsMenu = SettingsMenu(self, self.game_surface, self.save_manager)
        self.controls_menu: ControlsMenu = ControlsMenu(self.game_surface, self.save_manager)
        self.sound_menu: SoundMenu = SoundMenu(self.game_surface, self.save_manager)

        self.menu_screens: dict[str, object] = {
            constants.TITLE_SCREEN_NAME: self.title_screen,
            constants.SAVE_SELECTION_NAME: self.save_selection,
            constants.TRACK_SELECTION_NAME: self.track_selection,
            constants.CAR_SELECTION_NAME: self.car_selection,
            constants.DIFFICULTY_SELECTION_NAME: self.difficulty_selection,
            constants.SETTINGS_MENU_NAME: self.settings_menu,
            constants.CONTROLS_MENU_NAME: self.controls_menu,
            constants.SOUND_MENU_NAME: self.sound_menu
        }

        self.menu_screen_indices: dict[str, int] = {
            constants.TITLE_SCREEN_NAME: 0,
            constants.SAVE_SELECTION_NAME: 1,
            constants.TRACK_SELECTION_NAME: 2,
            constants.CAR_SELECTION_NAME: 3,
            constants.DIFFICULTY_SELECTION_NAME: 4,
            constants.RACE_SCREEN_NAME: 5,
            constants.SETTINGS_MENU_NAME: -1,
            constants.CONTROLS_MENU_NAME: -2,
            constants.SOUND_MENU_NAME: -3
        }
        self.current_screen: str = ""
        self.next_screen: str = ""
        self.ui_clock: pygame.time.Clock = pygame.time.Clock()

        self.custom_cursor_image: pygame.Surface = pygame.image.load(
            constants.GENERAL_IMAGE_PATH.format(name="cursor")).convert_alpha()
        self.custom_cursor_image = pygame.transform.scale(self.custom_cursor_image,
                                                          (constants.CURSOR_WIDTH, constants.CURSOR_HEIGHT))
        self.click_sound: pygame.mixer.Sound = pygame.mixer.Sound(constants.CLICK_SOUND_PATH)
        self.hover_sound: pygame.mixer.Sound = pygame.mixer.Sound(constants.HOVER_SOUND_PATH)

        # Apply volumes immediately
        self.save_manager.apply_all_settings()

        # Letterbox scaling
        self.scale_factor: float = 1.0
        self.offset_x: int = 0
        self.offset_y: int = 0

        # Race
        self.race: Race
        self.track_name: str = ""
        self.car_index: int = 0
        self.style_index: int = 0
        self.difficulty: str = ""

        # Transitions
        self.garage_door: pygame.Surface = utilities.load_image(constants.GENERAL_IMAGE_PATH.format(name="garage"),
                                                                False, constants.WIDTH, constants.HEIGHT)
        self.dark_overlay: pygame.Surface = pygame.Surface((constants.WIDTH, constants.HEIGHT), pygame.SRCALPHA)

    def set_save_slot_and_load(self, slot_index: int) -> None:
        """Sets the active save slot and re-initializes screens."""
        self.save_manager.set_save_slot(slot_index)

        # Re-create screens that depend on save_manager data
        from src.menus.save_selection import SaveSelection  # Re-import here just in case

        self.title_screen = TitleScreen(self, self.game_surface, self.save_manager)
        self.save_selection = SaveSelection(self, self.game_surface, self.save_manager)
        self.track_selection = TrackSelection(self, self.game_surface, self.save_manager)
        self.car_selection = CarSelection(self, self.game_surface, self.save_manager)
        self.difficulty_selection = DifficultySelection(self, self.game_surface, self.save_manager)
        self.settings_menu = SettingsMenu(self, self.game_surface, self.save_manager)
        self.controls_menu = ControlsMenu(self.game_surface, self.save_manager)
        self.sound_menu = SoundMenu(self.game_surface, self.save_manager)

        self.menu_screens = {
            constants.TITLE_SCREEN_NAME: self.title_screen,
            constants.SAVE_SELECTION_NAME: self.save_selection,
            constants.TRACK_SELECTION_NAME: self.track_selection,
            constants.CAR_SELECTION_NAME: self.car_selection,
            constants.DIFFICULTY_SELECTION_NAME: self.difficulty_selection,
            constants.SETTINGS_MENU_NAME: self.settings_menu,
            constants.CONTROLS_MENU_NAME: self.controls_menu,
            constants.SOUND_MENU_NAME: self.sound_menu
        }

    def set_track_name(self, track_name: str) -> None:
        self.track_name = track_name

    def set_difficulty(self, difficulty: str) -> None:
        self.difficulty = difficulty

    def set_car_style(self, car_index: int, style_index: int) -> None:
        self.car_index = car_index
        self.style_index = style_index

    def draw_letterboxed_surface(self) -> None:
        window_width, window_height = self.screen.get_size()
        if window_width == 0 or window_height == 0:
            return

        window_aspect: float = window_width / window_height
        game_aspect: float = constants.WIDTH / constants.HEIGHT

        new_width: int = window_width
        new_height: int = window_height
        if window_aspect > game_aspect:
            self.scale_factor = window_height / constants.HEIGHT
            new_width = int(constants.WIDTH * self.scale_factor)
        else:
            self.scale_factor = window_width / constants.WIDTH
            new_height = int(constants.HEIGHT * self.scale_factor)

        self.offset_x: int = (window_width - new_width) // 2
        self.offset_y: int = (window_height - new_height) // 2

        scaled_surface: pygame.Surface = pygame.transform.scale(self.game_surface, (new_width, new_height))
        self.screen.fill((0, 0, 0))
        self.screen.blit(scaled_surface, (self.offset_x, self.offset_y))

    def _play_intro_music(self):
        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.load(constants.GENERAL_AUDIO_PATH.format(song_name="intro"))
            pygame.mixer.music.set_volume(self.save_manager.get_volumes()["music"])
            pygame.mixer.music.play(-1)

    def _handle_events(self):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                utilities.quit_game()
            if event.type == pygame.VIDEORESIZE:
                self.screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)
        return events

    def start(self) -> None:
        pygame.mouse.set_visible(False)
        self._play_intro_music()
        if not self.title_screen.play_intro(self.screen):
            utilities.quit_game()
        pygame.mouse.set_visible(False)

        self.current_screen = self.title_screen.name
        running: bool = True
        while running:
            self._play_intro_music()
            events = self._handle_events()
            self.get_scaled_mouse_pos()

            next_action: str = constants.NO_ACTION_CODE
            if not self.menu_screens[self.current_screen].transitioning:
                next_action = self.menu_screens[self.current_screen].handle_events(events, self.scaled_mouse_pos)

            if next_action == constants.EXIT_GAME_CODE:
                utilities.quit_game()
            elif next_action != constants.NO_ACTION_CODE:
                self.click_sound.play()
                self.next_screen = next_action
                start_transition: bool = True
                backwards: bool = False if self.menu_screen_indices.get(self.next_screen,
                                                                        0) > self.menu_screen_indices.get(
                    self.current_screen, 0) else True
                self.menu_screens[self.current_screen].initialize_transition(start_transition=start_transition,
                                                                             backwards=backwards)

            if self.next_screen != "" and not self.menu_screens[self.current_screen].transitioning:
                if self.next_screen != constants.RACE_SCREEN_NAME:
                    start_transition: bool = False
                    backwards: bool = False if self.menu_screen_indices.get(self.next_screen,
                                                                            0) > self.menu_screen_indices.get(
                        self.current_screen, 0) else True

                    if self.current_screen == constants.SAVE_SELECTION_NAME:
                        self.save_selection.load_summaries()

                    self.menu_screens[self.next_screen].initialize_transition(start_transition=start_transition,
                                                                              backwards=backwards)
                    self.current_screen = self.next_screen
                    self.next_screen = ""
                else:
                    self._start_race()
                    # After race, reload screens to reflect unlocks
                    if self.save_manager.current_slot != -1:
                        # Use current_slot - 1 because set_save_slot_and_load expects 0-based index
                        # and adds 1 internally.
                        # self.save_manager.current_slot is 1-based (e.g. 1).
                        # So pass 0.
                        self.set_save_slot_and_load(self.save_manager.current_slot - 1)

                    self.current_screen = constants.TRACK_SELECTION_NAME
                    self.next_screen = ""

            self.menu_screens[self.current_screen].draw()
            self.draw_cursor()
            self.draw_letterboxed_surface()
            pygame.display.flip()
            self.ui_clock.tick(60)

    def get_scaled_mouse_pos(self) -> None:
        pos = pygame.mouse.get_pos()
        if self.scale_factor == 0:
            self._set_scaled_mouse_pos(x=0, y=0)
        else:
            game_x = (pos[0] - self.offset_x) / self.scale_factor
            game_y = (pos[1] - self.offset_y) / self.scale_factor
            self._set_scaled_mouse_pos(int(game_x), int(game_y))

    def _set_scaled_mouse_pos(self, x: int, y: int) -> None:
        self.scaled_mouse_pos = (x, y)

    def draw_cursor(self) -> None:
        if (0 <= self.scaled_mouse_pos[0] < constants.WIDTH and
                0 <= self.scaled_mouse_pos[1] < constants.HEIGHT):
            self.game_surface.blit(self.custom_cursor_image, self.scaled_mouse_pos)

    def _start_race(self) -> None:
        racing: bool = True
        while racing:
            self.race = Race(self, self.track_name, self.car_index, self.style_index, self.difficulty,
                             self.save_manager)
            racing = self.race.start()