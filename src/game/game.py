import pygame

from ..utilities import constants
from ..menus.car_selection import CarSelection
from ..menus.controls_menu import ControlsMenu
from ..menus.difficulty_selection import DifficultySelection
from ..utilities.save_manager import SaveManager
from ..menus.settings_menu import SettingsMenu
from ..menus.sound_menu import SoundMenu
from ..menus.title_screen import TitleScreen
from ..menus.save_selection import SaveSelection
from ..menus.track_selection import TrackSelection
from ..utilities import utilities
from .race import Race
from ..enums.difficulty import Difficulty
from ..enums.track_name import TrackName
from ..enums.game_state import GameState


class Game:
    """Manages the overall game state, main loop, and coordination between Car and Track"""

    width: int
    height: int
    screen: pygame.Surface
    game_surface: pygame.Surface
    ui_clock: pygame.time.Clock
    save_manager: SaveManager
    title_screen: TitleScreen
    save_selection: SaveSelection
    track_selection: TrackSelection
    car_selection: CarSelection
    difficulty_selection: DifficultySelection
    settings_menu: SettingsMenu
    controls_menu: ControlsMenu
    sound_menu: SoundMenu
    game_states: dict[GameState, tuple[object, int]]
    custom_cursor_image: pygame.Surface
    current_state: GameState | None
    next_state: GameState | None
    click_sound: pygame.mixer.Sound
    hover_sound: pygame.mixer.Sound
    scale_factor: float
    offset_x: int
    offset_y: int
    race: Race
    track_name: TrackName | None
    car_index: int
    style_index: int
    difficulty: Difficulty | None
    garage_door: pygame.Surface
    dark_overlay: pygame.Surface

    def __init__(self) -> None:

        # Initialize Pygame
        pygame.init()
        pygame.font.init()
        pygame.mixer.init()
        pygame.display.set_caption(constants.GAME_TITLE)

        # Create the window
        self.width = constants.WIDTH
        self.height = constants.HEIGHT
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
        self.game_surface = pygame.Surface((self.width, self.height))
        self.ui_clock = pygame.time.Clock()
        self.save_manager = SaveManager(0)

        # Create menu screens and initialize menu state variables
        self.title_screen = TitleScreen(self, self.game_surface, self.save_manager)
        self.save_selection = SaveSelection(self, self.game_surface, self.save_manager)
        self.track_selection = TrackSelection(self, self.game_surface, self.save_manager)
        self.car_selection = CarSelection(self, self.game_surface, self.save_manager)
        self.difficulty_selection  = DifficultySelection(self, self.game_surface, self.save_manager)
        self.settings_menu = SettingsMenu(self, self.game_surface, self.save_manager)
        self.controls_menu = ControlsMenu(self.game_surface, self.save_manager)
        self.sound_menu = SoundMenu(self.game_surface, self.save_manager)
        self.game_states: dict[str, tuple[object, int]] = {
            GameState.TITLE_MENU: (self.title_screen, 0),
            GameState.SAVE_FILE_MENU: (self.save_selection, 1),
            GameState.TRACK_SELECTION_MENU: (self.track_selection, 2),
            GameState.VEHICLE_SELECTION_MENU: (self.car_selection, 3),
            GameState.DIFFICULTY_SELECTION_MENU: (self.difficulty_selection, 4),
            GameState.SETTINGS_MENU: (self.settings_menu, -1),
            GameState.KEYBINDS_MENU: (self.controls_menu, -2),
            GameState.SOUND_MENU: (self.sound_menu, -3)
        }
        self.current_state = None
        self.next_state = None

        self.custom_cursor_image = pygame.image.load(constants.GENERAL_IMAGE_PATH.format(name="cursor")).convert_alpha()
        self.custom_cursor_image = pygame.transform.scale(self.custom_cursor_image, (constants.CURSOR_WIDTH, constants.CURSOR_HEIGHT))
        self.click_sound = pygame.mixer.Sound(constants.CLICK_SOUND_PATH)
        self.hover_sound = pygame.mixer.Sound(constants.HOVER_SOUND_PATH)

        # Apply volumes immediately
        self.save_manager.apply_all_settings()

        # Letterbox scaling
        self.scale_factor = 1.0
        self.offset_x = 0
        self.offset_y = 0

        # Race
        self.track_name = None
        self.car_index = 0
        self.style_index = 0
        self.difficulty = None

        # Transitions
        self.garage_door = utilities.load_image(constants.GENERAL_IMAGE_PATH.format(name="garage"), False, constants.WIDTH, constants.HEIGHT)
        self.dark_overlay = pygame.Surface((constants.WIDTH, constants.HEIGHT), pygame.SRCALPHA)

    def set_save_slot_and_load(self, slot_index: int) -> None:
        """Sets the active save slot and re-initializes screens."""
        self.save_manager.set_save_slot(slot_index)

        self.title_screen = TitleScreen(self, self.game_surface, self.save_manager)
        self.save_selection = SaveSelection(self, self.game_surface, self.save_manager)
        self.track_selection = TrackSelection(self, self.game_surface, self.save_manager)
        self.car_selection = CarSelection(self, self.game_surface, self.save_manager)
        self.difficulty_selection = DifficultySelection(self, self.game_surface, self.save_manager)
        self.settings_menu = SettingsMenu(self, self.game_surface, self.save_manager)
        self.controls_menu = ControlsMenu(self.game_surface, self.save_manager)
        self.sound_menu = SoundMenu(self.game_surface, self.save_manager)

        self.game_states: dict[str, tuple[object, int]] = {
            GameState.TITLE_MENU: (self.title_screen, 0),
            GameState.SAVE_FILE_MENU: (self.save_selection, 1),
            GameState.TRACK_SELECTION_MENU: (self.track_selection, 2),
            GameState.VEHICLE_SELECTION_MENU: (self.car_selection, 3),
            GameState.DIFFICULTY_SELECTION_MENU: (self.difficulty_selection, 4),
            GameState.SETTINGS_MENU: (self.settings_menu, -1),
            GameState.KEYBINDS_MENU: (self.controls_menu, -2),
            GameState.SOUND_MENU: (self.sound_menu, -3)
        }

    def set_track_name(self, track_name: TrackName) -> None:
        self.track_name = track_name

    def set_difficulty(self, difficulty: Difficulty) -> None:
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
            elif event.type == pygame.VIDEORESIZE:
                self.screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)
        return events

    def _is_transition_backwards(self) -> bool:
        current_index: int = self.game_states.get(self.current_state, [None, 0])[1]
        next_index: int = 100 if self.next_state == GameState.RACE_MENU else self.game_states.get(self.next_state, [None, 0])[1]
        return next_index <= current_index

    def start(self) -> None:
        pygame.mouse.set_visible(False)
        self._play_intro_music()
        if not self.title_screen.play_intro(self.screen):
            utilities.quit_game()
        pygame.mouse.set_visible(False)

        self.current_state = GameState.TITLE_MENU
        running: bool = True
        while running:
            self._play_intro_music()
            events = self._handle_events()
            self.set_scaled_mouse_pos()

            next_action: str = constants.NO_ACTION_CODE
            if not self.game_states[self.current_state][0].transitioning:
                next_action = self.game_states[self.current_state][0].handle_events(events, self.scaled_mouse_pos)

            if next_action == constants.EXIT_GAME_CODE:
                utilities.quit_game()
            elif next_action != constants.NO_ACTION_CODE:
                self.click_sound.play()
                self.next_state = next_action
                start_transition: bool = True
                backwards: bool = self._is_transition_backwards()
                self.game_states[self.current_state][0].initialize_transition(start_transition=start_transition, backwards=backwards)

            if self.next_state != None and not self.game_states[self.current_state][0].transitioning:
                if self.next_state != GameState.RACE_MENU:
                    start_transition: bool = False
                    backwards: bool = self._is_transition_backwards()

                    if self.current_state == GameState.SAVE_FILE_MENU:
                        self.save_selection.load_summaries()

                    self.game_states[self.next_state][0].initialize_transition(start_transition=start_transition, backwards=backwards)
                    self.current_state = self.next_state
                    self.next_state = None
                else:
                    self._start_race()
                    if self.save_manager.current_slot != -1:
                        self.set_save_slot_and_load(self.save_manager.current_slot - 1)

                    self.current_state = GameState.TRACK_SELECTION_MENU
                    self.next_state = None

            self.game_states[self.current_state][0].draw()
            self.draw_cursor()
            self.draw_letterboxed_surface()
            pygame.display.flip()
            self.ui_clock.tick(60)

    def set_scaled_mouse_pos(self) -> None:
        game_x = 0
        game_y = 0
        pos = pygame.mouse.get_pos()
        if self.scale_factor != 0:
            game_x = (pos[0] - self.offset_x) / self.scale_factor
            game_y = (pos[1] - self.offset_y) / self.scale_factor
        self.scaled_mouse_pos = (int(game_x), int(game_y))

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