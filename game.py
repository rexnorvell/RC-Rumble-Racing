import sys

import pygame

import constants
from title_screen import TitleScreen
from track_selection import TrackSelection
from race import Race


class Game:
    # Manages the overall game state, main loop, and coordination between Car and Track
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

        # Menu screens
        self.title_screen: TitleScreen
        self.track_selection: TrackSelection
        self.custom_cursor_image: pygame.Surface = pygame.image.load(constants.CURSOR_IMAGE_PATH).convert_alpha()
        self.custom_cursor_image = pygame.transform.scale(self.custom_cursor_image,
                                                          (constants.CURSOR_WIDTH, constants.CURSOR_HEIGHT))
        self.click_sound: pygame.mixer.Sound = pygame.mixer.Sound(constants.CLICK_SOUND_PATH)
        self.click_sound.set_volume(0.2)

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

        game_width = constants.WIDTH
        game_height = constants.HEIGHT

        # Calculate aspect ratios
        window_aspect = window_width / window_height
        game_aspect = game_width / game_height

        # Determine scaling factor
        if window_aspect > game_aspect:
            # Window is wider than game
            self.scale_factor = window_height / game_height
            new_height = window_height
            new_width = int(game_width * self.scale_factor)
        else:
            # Window is taller than game
            self.scale_factor = window_width / game_width
            new_width = window_width
            new_height = int(game_height * self.scale_factor)

        # Calculate offsets for centering
        self.offset_x = (window_width - new_width) // 2
        self.offset_y = (window_height - new_height) // 2

        # Scale and blit
        scaled_surface = pygame.transform.scale(self.game_surface, (new_width, new_height))
        self.screen.fill((0, 0, 0))  # Fill with black bars
        self.screen.blit(scaled_surface, (self.offset_x, self.offset_y))

    def _set_title_screen(self):
        self.title_screen = TitleScreen(self.game_surface)

    def welcome(self) -> None:
        """Displays the title screen and displays the track selection screen when the button is clicked"""

        pygame.mouse.set_visible(False)
        pygame.mixer.music.load(constants.GENERAL_AUDIO_PATH.format(song_name="intro"))
        pygame.mixer.music.play(-1)
        self._set_title_screen()
        title_clock: pygame.time.Clock = pygame.time.Clock()
        if not self.title_screen.play_intro(self.screen):
            self.quit()
        pygame.mouse.set_visible(False)

        running = True
        while running:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.quit()
                if event.type == pygame.VIDEORESIZE:
                    self.screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)

            # Get scaled mouse position *once* per frame
            self.get_scaled_mouse_pos()

            next_action = self.title_screen.handle_events(events, self.scaled_mouse_pos)

            if next_action == "exit":
                self.quit()
            elif next_action == "track_selection":
                self.click_sound.play()
                running = False

            self.title_screen.draw()
            self.draw_cursor()

            # Draw the letterboxed game_surface to the screen
            self.draw_letterboxed_surface()
            pygame.display.flip()
            title_clock.tick(60)

        # After the loop, go to track selection
        self._track_select()

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
        if self.scaled_mouse_pos[0] not in [0, constants.WIDTH - 1] and self.scaled_mouse_pos[1] not in [0, constants.HEIGHT - 1]:
            self.game_surface.blit(self.custom_cursor_image, self.scaled_mouse_pos)

    def _track_select(self) -> None:
        """Displays the track selection screen and starts the game once a track is selected"""
        self.track_selection = TrackSelection(self.game_surface)
        track_select_clock: pygame.time.Clock = pygame.time.Clock()

        running = True
        while running:
            if not pygame.mixer.music.get_busy():
                pygame.mixer.music.load(constants.GENERAL_AUDIO_PATH.format(song_name="intro"))
                pygame.mixer.music.play(-1)
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.quit()
                if event.type == pygame.VIDEORESIZE:
                    self.screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)

            self.get_scaled_mouse_pos()
            self.draw_cursor()

            next_action = self.track_selection.handle_events(events, self.scaled_mouse_pos)

            if next_action == "exit":
                self.quit()
            elif next_action != "":
                self.click_sound.play()
                track_name = next_action
                racing: bool = True
                while racing:
                    self.race = Race(self, track_name, 0, 1)
                    racing = self.race.start()

            self.track_selection.draw()
            self.draw_cursor()

            # Draw the letterboxed game_surface to the screen
            self.draw_letterboxed_surface()
            pygame.display.flip()
            track_select_clock.tick(60)

    def quit(self) -> None:
        #Quits the game
        pygame.quit()
        sys.exit()