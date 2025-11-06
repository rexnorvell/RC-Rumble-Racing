import csv
import json
from pathlib import Path
import sys
from typing import Optional

import pygame

import constants
from car import Car
from track import Track
from title_screen import TitleScreen
from track_selection import TrackSelection


class Game:
    """Manages the overall game state, main loop, and coordination between Car and Track."""

    def __init__(self) -> None:
        pygame.init()
        pygame.font.init()
        pygame.mixer.init()

        self.screen: pygame.Surface = pygame.display.set_mode((1024, 576), pygame.RESIZABLE)
        self.game_surface: pygame.Surface = pygame.Surface((constants.WIDTH, constants.HEIGHT))
        self.clock: pygame.time.Clock = pygame.time.Clock()
        pygame.display.set_caption(constants.GAME_TITLE)

        # Track and car
        self.track: Track
        self.personal_best_time: float
        self.fastest_lap_record: float = float("inf")  # All-time fastest lap
        self.car: Car
        self.car_sprite: pygame.Surface
        self.car_type_index = 0

        # Ghost
        self.show_ghost: bool = True
        self.found_ghost: bool = False
        self.ghost_done: bool = False
        self.ghost_car: Car
        self.ghost_car_sprite: pygame.Surface
        self.ghost_filename: str

        # Menu screens
        self.title_screen: TitleScreen
        self.track_selection: TrackSelection
        self.custom_cursor_image: pygame.Surface = pygame.image.load(constants.CURSOR_IMAGE_PATH).convert_alpha()
        self.custom_cursor_image = pygame.transform.scale(self.custom_cursor_image,
                                                          (constants.CURSOR_WIDTH, constants.CURSOR_HEIGHT))
        self.click_sound: pygame.mixer.Sound = pygame.mixer.Sound(constants.CLICK_SOUND_PATH)
        self.click_sound.set_volume(0.2)

        # State
        self.current_lap: int = 1
        self.has_checkpoint: bool = False
        self.before_race: bool = True
        self.during_race: bool = False
        self.race_over: bool = False
        self.applause_played: bool = False
        self.current_track_index: int = 0
        self.race_start_time: Optional[int] = None
        self.race_end_time: Optional[int] = None
        self.countdown_start_time: int = 0

        # Lap Timers
        self.lap_start_time: Optional[int] = None
        self.lap_times: list[int] = []
        self.fastest_lap_in_race: Optional[int] = None  # Fastest lap this race
        self.timer_font: pygame.font.Font = pygame.font.Font(constants.TEXT_FONT_PATH, 30)

        # Sounds
        self.next_lap_sound = pygame.mixer.Sound(
            constants.TRACK_AUDIO_PATH.format(track_name="general", song_type="next_lap"))
        self.next_lap_sound.set_volume(0.5)

        # Fonts
        self.countdown_font: pygame.font.Font = pygame.font.Font(constants.TEXT_FONT_PATH, 120)

        # Pause state
        self.is_paused: bool = False
        self.pause_start_time: int = 0  # Used to refund time spent paused
        self.pause_hover_index: int = 0  # 0=None, 1=Resume, 2=Replay, 3=Exit

        # Pause menu fonts
        self.pause_title_font: pygame.font.Font = pygame.font.Font(constants.TEXT_FONT_PATH, 80)
        self.pause_button_font: pygame.font.Font = pygame.font.Font(constants.TEXT_FONT_PATH, 50)

        # Pause menu overlay
        self.pause_overlay: pygame.Surface = pygame.Surface((constants.WIDTH, constants.HEIGHT), pygame.SRCALPHA)
        self.pause_overlay.fill(constants.PAUSE_OVERLAY_COLOR)

        # Pause menu button rects
        button_x: float = (constants.WIDTH - constants.PAUSE_BUTTON_WIDTH) / 2
        self.resume_button_rect: pygame.Rect = pygame.Rect(button_x, constants.PAUSE_RESUME_Y,
                                                           constants.PAUSE_BUTTON_WIDTH, constants.PAUSE_BUTTON_HEIGHT)
        self.replay_button_rect: pygame.Rect = pygame.Rect(button_x, constants.PAUSE_REPLAY_Y,
                                                           constants.PAUSE_BUTTON_WIDTH, constants.PAUSE_BUTTON_HEIGHT)
        self.exit_button_rect: pygame.Rect = pygame.Rect(button_x, constants.PAUSE_EXIT_Y, constants.PAUSE_BUTTON_WIDTH,
                                                         constants.PAUSE_BUTTON_HEIGHT)

        # Race over menu state
        self.race_over_hover_index: int = 0  # 0=None, 1=Retry, 2=Exit

        # Race over menu button rects
        race_over_button_x: float = (constants.WIDTH - constants.RACE_OVER_BUTTON_WIDTH) / 2
        self.retry_button_rect: pygame.Rect = pygame.Rect(race_over_button_x, constants.RACE_OVER_RETRY_Y,
                                                          constants.RACE_OVER_BUTTON_WIDTH,
                                                          constants.RACE_OVER_BUTTON_HEIGHT)
        self.exit_race_over_button_rect: pygame.Rect = pygame.Rect(race_over_button_x, constants.RACE_OVER_EXIT_Y,
                                                                   constants.RACE_OVER_BUTTON_WIDTH,
                                                                   constants.RACE_OVER_BUTTON_HEIGHT)

        # Letterbox scaling
        self.scale_factor: float = 1.0
        self.offset_x: int = 0
        self.offset_y: int = 0

    def _draw_letterboxed_surface(self) -> None:
        """Calculates letterbox scaling and blits the game_surface to the screen."""
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
            # Window is wider than game (pillarbox)
            self.scale_factor = window_height / game_height
            new_height = window_height
            new_width = int(game_width * self.scale_factor)
        else:
            # Window is taller than game (letterbox)
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

    def _scale_mouse_pos(self, pos: tuple[int, int]) -> tuple[int, int]:
        """Scales mouse position from window coordinates to game_surface coordinates."""
        if self.scale_factor == 0:  # Prevent divide-by-zero
            return 0, 0

        # Un-scale and un-offset the mouse position
        game_x = (pos[0] - self.offset_x) / self.scale_factor
        game_y = (pos[1] - self.offset_y) / self.scale_factor

        return int(game_x), int(game_y)

    def _format_time_simple(self, time_ms: int) -> str:
        """Formats time in MM:SS:ms."""
        if time_ms < 0:
            return "--:--:--"
        total_seconds: float = time_ms / 1000.0
        minutes: int = int(total_seconds // 60)
        seconds: int = int(total_seconds % 60)
        milliseconds: int = int((time_ms % 1000) // 10)
        return f"{minutes:02}:{seconds:02}:{milliseconds:02}"

    def _play_next_track(self) -> None:
        """Loads and plays the next audio track in the playlist."""
        if self.current_track_index < len(self.track.playlist):
            track_path, loops = self.track.playlist[self.current_track_index]
            pygame.mixer.music.load(track_path)
            pygame.mixer.music.play(loops)
            self.current_track_index += 1

    def _draw_countdown(self, current_time: int) -> None:
        """Calculates and draws the pre-race countdown timer."""
        elapsed: int = current_time - self.countdown_start_time
        countdown_text: Optional[str] = None

        if elapsed < 1000:
            countdown_text = "3"
        elif elapsed < 2000:
            countdown_text = "2"
        elif elapsed < 3000:
            countdown_text = "1"
        elif elapsed < 4000:
            if not self.during_race:
                self.during_race = True
                self.race_start_time = pygame.time.get_ticks()
                self.lap_start_time = self.race_start_time
            countdown_text = "Go!"
        else:
            self.before_race = False

        if countdown_text:
            countdown_surface: pygame.Surface = self.countdown_font.render(countdown_text, True, constants.TEXT_COLOR)
            countdown_rect: pygame.Rect = countdown_surface.get_rect(
                center=(constants.WIDTH / 2, constants.HEIGHT / 2))
            self.game_surface.blit(countdown_surface, countdown_rect)

    def _display_race_time(self) -> float:
        """Draws the final race time after the race is over."""
        if self.race_start_time is None or self.race_end_time is None:
            return sys.float_info.max

        total_time_ms: int = self.race_end_time - self.race_start_time
        total_seconds: float = total_time_ms / 1000
        formatted_time: str = f"{total_seconds:.2f} s"

        time_font: pygame.font.Font = pygame.font.Font(constants.TEXT_FONT_PATH, 60)
        time_surface: pygame.Surface = time_font.render(formatted_time, True, constants.TEXT_COLOR)
        time_rect: pygame.Rect = time_surface.get_rect(center=(constants.WIDTH / 2, 325))
        self.game_surface.blit(time_surface, time_rect)

        return total_seconds

    def _check_lap_completion(self) -> None:
        """Checks for checkpoint and finish line crosses and updates lap count."""
        if self.track.check_checkpoint(self.car.x, self.car.y):
            self.has_checkpoint = True

        if self.has_checkpoint and self.track.check_finish_line(self.car.x, self.car.y):
            self.has_checkpoint = False

            if self.lap_start_time:
                current_time: int = pygame.time.get_ticks()
                lap_time_ms: int = current_time - self.lap_start_time
                self.lap_times.append(lap_time_ms)
                self.lap_start_time = current_time

                # Update fastest lap in this race
                if self.fastest_lap_in_race is None or lap_time_ms < self.fastest_lap_in_race:
                    self.fastest_lap_in_race = lap_time_ms

            self.current_lap += 1

            if self.current_lap > constants.NUM_LAPS[self.track.name]:
                self.during_race = False
                self.race_over = True
                self.race_end_time = pygame.time.get_ticks()
                self.lap_start_time = None
            else:
                if self.current_lap == constants.NUM_LAPS[self.track.name]:
                    self._play_next_track()
                else:
                    self.next_lap_sound.play()

    def welcome(self) -> None:
        """Displays the title screen and displays the track selection screen when the button is clicked."""
        # Re-hide the mouse in case the video player showed it
        pygame.mouse.set_visible(False)

        pygame.mixer.music.load(constants.GENERAL_AUDIO_PATH.format(song_name="intro"))
        pygame.mixer.music.play(-1)
        self.title_screen = TitleScreen(self.game_surface)
        title_clock: pygame.time.Clock = pygame.time.Clock()
        if not self.title_screen.play_intro(self.screen):
            self._quit()

        running = True
        while running:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self._quit()
                if event.type == pygame.VIDEORESIZE:
                    self.screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)

            # Get scaled mouse position *once* per frame
            unscaled_mouse_pos = pygame.mouse.get_pos()
            scaled_mouse_pos = self._scale_mouse_pos(unscaled_mouse_pos)

            next_action = self.title_screen.handle_events(events, scaled_mouse_pos)

            if next_action == "exit":
                self._quit()
            elif next_action == "track_selection":
                self.click_sound.play()
                running = False  # Exit the welcome loop

            self.title_screen.draw()
            self._draw_cursor(scaled_mouse_pos)

            # Draw the letterboxed game_surface to the screen
            self._draw_letterboxed_surface()
            pygame.display.flip()
            title_clock.tick(60)

        # After the loop, go to track selection
        self._track_select()

    def _draw_cursor(self, mouse_pos: tuple[int, int]) -> None:
        """Draws the custom cursor on the game surface."""
        # Use the already-scaled mouse_pos
        if mouse_pos[0] not in [0, constants.WIDTH - 1] and mouse_pos[1] not in [0, constants.HEIGHT - 1]:
            self.game_surface.blit(self.custom_cursor_image, mouse_pos)

    def _track_select(self) -> None:
        """Displays the track selection screen and starts the game a track is selected."""
        self.track_selection = TrackSelection(self.game_surface)
        track_select_clock: pygame.time.Clock = pygame.time.Clock()
        running = True

        # Make sure intro music is playing when we first enter this screen
        pygame.mixer.music.load(constants.GENERAL_AUDIO_PATH.format(song_name="intro"))
        pygame.mixer.music.play(-1)

        running = True
        while running:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self._quit()
                if event.type == pygame.VIDEORESIZE:
                    self.screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)

            # Get scaled mouse position *once* per frame
            unscaled_mouse_pos = pygame.mouse.get_pos()
            scaled_mouse_pos = self._scale_mouse_pos(unscaled_mouse_pos)

            next_action = self.track_selection.handle_events(events, scaled_mouse_pos)

            if next_action == "exit":
                self._quit()
            elif next_action != "":
                self.click_sound.play()
                track_name_to_load = next_action

                while True:
                    self._reset_game_state()

                    self.track = Track(track_name_to_load)
                    self.car = Car(self.game_surface, self.track.name, is_ghost=False)

                    run_action = self._run()

                    if run_action == "replay":
                        # No need to reset here, loop will do it
                        continue
                    else:
                        # "exit_to_menu" or normal race finish
                        # No need to reset here, we are breaking
                        break

            self.track_selection.draw()
            self._draw_cursor(scaled_mouse_pos)

            # Draw the letterboxed game_surface to the screen
            self._draw_letterboxed_surface()
            pygame.display.flip()
            track_select_clock.tick(60)

    def _get_personal_best_time(self) -> None:
        """Get the user's personal best time for the current track."""
        personal_best_metadata_path: Path = Path(
            constants.PERSONAL_BEST_METADATA_FILE_PATH.format(track_name=self.track.name))
        best_time: float = float("inf")
        best_lap: float = float("inf")
        if personal_best_metadata_path.exists():
            with open(personal_best_metadata_path, "r") as personal_best:
                personal_best_data = json.load(personal_best)
            best_time = personal_best_data.get("time", float("inf"))
            best_lap = personal_best_data.get("fastest_lap", float("inf"))

        self.personal_best_time = best_time
        self.fastest_lap_record = best_lap

    def _run(self) -> str:
        """The main game loop when the user is racing on a track. Returns an action string."""

        # Flags
        found_ghost: bool = False
        running: bool = True
        compared_to_best: bool = False

        # Initialization
        self._get_personal_best_time()
        self._create_replay_file()
        if self.show_ghost:
            found_ghost = self._get_ghost_info()
        next_ghost_index: int = 1
        self.car_sprite = pygame.image.load(
            constants.CAR_IMAGE_PATH.format(car_type=constants.CAR_TYPES[self.car_type_index])).convert_alpha()
        self.car_sprite = pygame.transform.scale(self.car_sprite, (self.car.width, self.car.height))
        self.countdown_start_time = pygame.time.get_ticks()
        self._play_next_track()

        # Main loop
        while running:
            self.clock.tick(60)
            current_time: int = pygame.time.get_ticks()
            events = pygame.event.get()

            # Get scaled mouse position *once* per frame
            unscaled_mouse_pos = pygame.mouse.get_pos()
            scaled_mouse_pos = self._scale_mouse_pos(unscaled_mouse_pos)

            # --- FLAG TO PREVENT EVENT CONFLICT ---
            just_paused: bool = False

            # --- CONSOLIDATED EVENT LOOP ---
            for event in events:
                if event.type == pygame.QUIT:
                    self._quit()
                elif event.type == pygame.KEYDOWN:

                    if event.key == pygame.K_ESCAPE:
                        # Prevent pausing if race is over
                        if not self.race_over:
                            self.is_paused = not self.is_paused
                            if self.is_paused:
                                # Just Paused
                                pygame.mixer.music.pause()
                                self.pause_start_time = pygame.time.get_ticks()
                                self.pause_hover_index = 0
                                just_paused = True  # <--- SET THE FLAG
                            else:
                                # Just Un-paused (by Esc)
                                pygame.mixer.music.unpause()

                                pause_duration = pygame.time.get_ticks() - self.pause_start_time
                                self.countdown_start_time += pause_duration
                                if self.race_start_time is not None:
                                    self.race_start_time += pause_duration

                    if event.key == pygame.K_g and not self.is_paused:
                        self.show_ghost = not self.show_ghost
                if event.type == pygame.VIDEORESIZE:
                    self.screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)

            # --- PAUSE LOGIC ---
            if self.is_paused and not just_paused:  # <--- CHECK THE FLAG
                pause_action = self._handle_pause_menu(events, scaled_mouse_pos)

                if pause_action == "resume":
                    self.is_paused = False
                    pygame.mixer.music.unpause()

                    pause_duration = pygame.time.get_ticks() - self.pause_start_time
                    self.countdown_start_time += pause_duration
                    if self.race_start_time is not None:
                        self.race_start_time += pause_duration

                    continue
                elif pause_action == "replay":
                    return "replay"
                elif pause_action == "exit_to_menu":
                    pygame.mixer.music.stop()
                    pygame.mixer.music.load(constants.GENERAL_AUDIO_PATH.format(song_name="intro"))
                    pygame.mixer.music.play(-1)
                    return "exit_to_menu"

            elif self.is_paused and just_paused:
                pass  # We will draw the menu later

            # --- REGULAR GAME LOGIC (if not paused) ---
            if not self.is_paused:
                if not pygame.mixer.music.get_busy() and not self.race_over:
                    self._play_next_track()

                keys: pygame.key.ScancodeWrapper = pygame.key.get_pressed()
                self.car.handle_input(keys, self.during_race)

                max_speed: float = constants.MAX_SPEED
                if self.track.is_off_road(self.car.x, self.car.y):
                    max_speed *= 0.5

                self.car.update_position(max_speed)

                self.track.draw(self.game_surface)

                # --- Draw New Race UI ---
                self._draw_race_ui(current_time)

                if self.before_race:
                    self._draw_countdown(current_time)
                if self.during_race:
                    elapsed_time: float = (current_time - self.race_start_time) / 1000
                    self._check_lap_completion()
                    if elapsed_time < self.personal_best_time:
                        self._log_car_properties()
                    if found_ghost and self.show_ghost and not self.ghost_done:
                        self.ghost_done = self._draw_ghost(next_ghost_index, self.ghost_car_sprite)
                    next_ghost_index += 1

                elif self.race_over:
                    # Run one-time actions
                    if not compared_to_best:
                        # Call _display_race_time *once* to get the final time
                        total_time: float = self._display_race_time()
                        self._compare_to_best(total_time)
                        compared_to_best = True
                    if not self.applause_played:
                        self.applause_played = True
                        self._play_next_track()

                    # Keep drawing the final time
                    self._display_race_time()

                    # Handle menu input
                    race_over_action = self._handle_race_over_menu(events, scaled_mouse_pos)
                    if race_over_action == "replay":
                        return "replay"
                    elif race_over_action == "exit_to_menu":
                        pygame.mixer.music.stop()
                        pygame.mixer.music.load(constants.GENERAL_AUDIO_PATH.format(song_name="intro"))
                        pygame.mixer.music.play(-1)
                        return "exit_to_menu"

                self.car.draw(self.car_sprite)

            # --- DRAW OVERLAYS ---
            if self.is_paused:
                self._draw_pause_menu()

            # Draw the race over menu if the race is over (and not paused)
            if self.race_over and not self.is_paused:
                self._draw_race_over_menu()
            # --- END DRAW CALL ---

            # Only draw the cursor if we are in a menu
            if self.is_paused or self.race_over:
                self._draw_cursor(scaled_mouse_pos)

            # Draw the letterboxed game_surface to the screen
            self._draw_letterboxed_surface()
            pygame.display.flip()

        # Default exit action
        pygame.mixer.music.stop()
        pygame.mixer.music.load(constants.GENERAL_AUDIO_PATH.format(song_name="intro"))
        pygame.mixer.music.play(-1)
        return "exit_to_menu"

    def _draw_race_ui(self, current_time: int) -> None:
        """Draws the main race UI elements (lap, times) onto the game surface."""

        # --- Top Left UI ---

        # Lap Counter
        if self.race_over:
            lap_str = "Finish!"
        else:
            lap_str = f"Lap {self.current_lap}/{constants.NUM_LAPS[self.track.name]}"

        # Total Time
        total_time_ms = -1
        if self.race_start_time:
            if self.race_over and self.race_end_time:
                total_time_ms = self.race_end_time - self.race_start_time
            else:
                total_time_ms = current_time - self.race_start_time
        total_time_str = f"Total Time {self._format_time_simple(total_time_ms)}"

        # --- Top Right UI ---

        # Total Record
        total_record_ms = -1
        if self.personal_best_time != float("inf"):
            total_record_ms = int(self.personal_best_time * 1000)
        total_record_str = f"Total Record {self._format_time_simple(total_record_ms)}"

        # Fastest Lap Record
        fastest_lap_ms = -1
        if self.fastest_lap_record != float("inf"):
            fastest_lap_ms = int(self.fastest_lap_record * 1000)
        fastest_lap_str = f"Fastest Lap {self._format_time_simple(fastest_lap_ms)}"

        # --- Render and Blit ---
        lap_surf = self.timer_font.render(lap_str, True, constants.TEXT_COLOR)
        total_time_surf = self.timer_font.render(total_time_str, True, constants.TEXT_COLOR)

        total_record_surf = self.timer_font.render(total_record_str, True, constants.TEXT_COLOR)
        fastest_lap_surf = self.timer_font.render(fastest_lap_str, True, constants.TEXT_COLOR)

        # Blit Top Left
        self.game_surface.blit(lap_surf, (20, 130))
        self.game_surface.blit(total_time_surf, (20, 165))

        # Blit Lap List
        num_laps = constants.NUM_LAPS[self.track.name]
        y_offset = 200  # Start below Total Time

        for i in range(num_laps):
            lap_num = i + 1
            lap_str = ""

            if i < len(self.lap_times):  # Completed lap
                lap_str += self._format_time_simple(self.lap_times[i])
            elif i == self.current_lap - 1 and self.lap_start_time:  # Current lap
                current_lap_ms = current_time - self.lap_start_time
                lap_str += self._format_time_simple(current_lap_ms)
            else:  # Future lap
                lap_str += "--:--:--"

            lap_list_surf = self.timer_font.render(lap_str, True, constants.TEXT_COLOR)
            self.game_surface.blit(lap_list_surf, (20, y_offset))
            y_offset += 35

        # Blit Top Right
        self.game_surface.blit(total_record_surf, (constants.WIDTH - total_record_surf.get_width() - 20, 20))
        self.game_surface.blit(fastest_lap_surf, (constants.WIDTH - fastest_lap_surf.get_width() - 20, 55))

    def _reset_game_state(self) -> None:
        """Resets the variables storing the game's state after the track is complete."""
        self.current_lap = 1
        self.has_checkpoint = False
        self.before_race = True
        self.during_race = False
        self.race_over = False
        self.applause_played = False
        self.current_track_index = 0
        self.race_start_time = None
        self.race_end_time = None
        self.countdown_start_time = 0
        self.show_ghost = True
        self.ghost_done = False
        self.is_paused = False
        self.lap_start_time = None
        self.lap_times = []
        self.fastest_lap_in_race = None
        self.race_over_hover_index = 0

    def _handle_pause_menu(self, events, mouse_pos: tuple[int, int]) -> str:
        """Handles input for the pause menu."""
        # Note: mouse_pos is already scaled

        # Check hover
        if self.resume_button_rect.collidepoint(mouse_pos):
            self.pause_hover_index = 1
        elif self.replay_button_rect.collidepoint(mouse_pos):
            self.pause_hover_index = 2
        elif self.exit_button_rect.collidepoint(mouse_pos):
            self.pause_hover_index = 3
        else:
            self.pause_hover_index = 0

        for event in events:
            if event.type == pygame.QUIT:
                self._quit()

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if self.pause_hover_index == 1:
                    self.click_sound.play()
                    return "resume"
                elif self.pause_hover_index == 2:
                    self.click_sound.play()
                    return "replay"
                elif self.pause_hover_index == 3:
                    self.click_sound.play()
                    return "exit_to_menu"
        return ""

    def _draw_pause_menu(self) -> None:
        """Draws the pause menu overlay and buttons onto the game_surface."""
        # Draw the semi-transparent overlay
        self.game_surface.blit(self.pause_overlay, (0, 0))

        # Draw Title
        title_text = self.pause_title_font.render("Paused", True, constants.PAUSE_TITLE_COLOR)
        title_rect = title_text.get_rect(center=(constants.WIDTH / 2, constants.PAUSE_TITLE_Y))
        self.game_surface.blit(title_text, title_rect)

        # Determine button colors based on hover
        resume_color = constants.PAUSE_BUTTON_HOVER_COLOR if self.pause_hover_index == 1 else constants.PAUSE_BUTTON_COLOR
        replay_color = constants.PAUSE_BUTTON_HOVER_COLOR if self.pause_hover_index == 2 else constants.PAUSE_BUTTON_COLOR
        exit_color = constants.PAUSE_BUTTON_HOVER_COLOR if self.pause_hover_index == 3 else constants.PAUSE_BUTTON_COLOR

        # Create and draw button text
        resume_text = self.pause_button_font.render("Resume", True, resume_color)
        replay_text = self.pause_button_font.render("Replay", True, replay_color)
        exit_text = self.pause_button_font.render("Exit to Menu", True, exit_color)

        self.game_surface.blit(resume_text, resume_text.get_rect(center=self.resume_button_rect.center))
        self.game_surface.blit(replay_text, replay_text.get_rect(center=self.replay_button_rect.center))
        self.game_surface.blit(exit_text, exit_text.get_rect(center=self.exit_button_rect.center))

    def _handle_race_over_menu(self, events, mouse_pos: tuple[int, int]) -> str:
        """Handles input for the race over menu."""
        # Note: mouse_pos is already scaled

        # Check hover
        if self.retry_button_rect.collidepoint(mouse_pos):
            self.race_over_hover_index = 1
        elif self.exit_race_over_button_rect.collidepoint(mouse_pos):
            self.race_over_hover_index = 2
        else:
            self.race_over_hover_index = 0

        for event in events:
            if event.type == pygame.QUIT:
                self._quit()

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if self.race_over_hover_index == 1:
                    self.click_sound.play()
                    return "replay"
                elif self.race_over_hover_index == 2:
                    self.click_sound.play()
                    return "exit_to_menu"
        return ""

    def _draw_race_over_menu(self) -> None:
        """Draws the race over menu buttons onto the game_surface."""
        # Note: This menu does *not* draw the dark overlay, so the
        # final time and track are visible underneath.

        # Draw Title
        title_text = self.pause_title_font.render("Race Finished!", True, constants.RACE_OVER_TITLE_COLOR)
        title_rect = title_text.get_rect(center=(constants.WIDTH / 2, constants.RACE_OVER_TITLE_Y))
        self.game_surface.blit(title_text, title_rect)

        # Determine button colors based on hover
        retry_color = constants.RACE_OVER_BUTTON_HOVER_COLOR if self.race_over_hover_index == 1 else constants.RACE_OVER_BUTTON_COLOR
        exit_color = constants.RACE_OVER_BUTTON_HOVER_COLOR if self.race_over_hover_index == 2 else constants.RACE_OVER_BUTTON_COLOR

        # Create and draw button text
        retry_text = self.pause_button_font.render("Retry", True, retry_color)
        exit_text = self.pause_button_font.render("Exit to Menu", True, exit_color)

        self.game_surface.blit(retry_text, retry_text.get_rect(center=self.retry_button_rect.center))
        self.game_surface.blit(exit_text, exit_text.get_rect(center=self.exit_race_over_button_rect.center))

    def _create_replay_file(self) -> None:
        """Creates a new .csv file when the race begins to log the user's car position."""
        with open(constants.REPLAY_FILE_PATH.format(track_name=self.track.name), "w", newline=""):
            pass

    def _get_ghost_info(self) -> bool:
        """Set ghost parameters and return True if the ghost file was found."""
        self.ghost_car = Car(self.game_surface, self.track.name, is_ghost=True)
        self.ghost_filename = constants.PERSONAL_BEST_FILE_PATH.format(track_name=self.track.name)
        self.ghost_car_sprite = pygame.image.load(
            constants.CAR_IMAGE_PATH.format(car_type=constants.CAR_TYPES[self.car_type_index])).convert_alpha()
        self.ghost_car_sprite = pygame.transform.scale(self.ghost_car_sprite,
                                                       (self.ghost_car.width, self.ghost_car.height))
        return Path(self.ghost_filename).exists()

    def _compare_to_best(self, total_time: float) -> None:
        """Compare the current time to the personal best, and if it was beaten, replace the personal best."""
        personal_best_metadata_path: Path = Path(
            constants.PERSONAL_BEST_METADATA_FILE_PATH.format(track_name=self.track.name))
        current_race_file: Path = Path(constants.REPLAY_FILE_PATH.format(track_name=self.track.name))

        # Check for new fastest lap in this race
        current_fastest_lap_ms = min(self.lap_times) if self.lap_times else float("inf")
        current_fastest_lap_sec = current_fastest_lap_ms / 1000.0

        is_new_total_record = total_time < self.personal_best_time
        is_new_lap_record = current_fastest_lap_sec < self.fastest_lap_record

        # Only save if we set a new *total time* record
        if is_new_total_record:
            metadata = {
                "time": total_time,
                "car_type_index": self.car_type_index
            }
            # If it's a new total record, save the fastest lap from *this* race
            # This also handles setting the first-ever fastest lap
            if self.lap_times:
                metadata["fastest_lap"] = current_fastest_lap_sec

            with open(personal_best_metadata_path, "w") as personal_best:
                json.dump(metadata, personal_best)

            if current_race_file.exists():
                new_personal_best: Path = current_race_file.with_name(constants.PERSONAL_BEST_FILE_NAME)
                # Use .replace() to overwrite the destination file if it exists
                current_race_file.replace(new_personal_best)

        # If we *only* set a new lap record (but not total time), save it
        elif is_new_lap_record:
            # Load existing data, update, and save
            metadata = {}
            if personal_best_metadata_path.exists():
                with open(personal_best_metadata_path, "r") as f:
                    metadata = json.load(f)

            metadata["fastest_lap"] = current_fastest_lap_sec  # Update fastest lap
            with open(personal_best_metadata_path, "w") as personal_best:
                json.dump(metadata, personal_best)

        # If no records, delete the replay file
        elif current_race_file.exists():
            current_race_file.unlink()


    def _draw_ghost(self, next_ghost_index: int, ghost_car_sprite: pygame.Surface) -> bool:
        """Retrieves the ghost's position at this frame and draws it on the screen, returning False if the ghost has finished the race."""
        found: bool = False
        with open(self.ghost_filename, newline="") as ghost_file:
            reader = csv.reader(ghost_file)
            for i, row in enumerate(reader):
                if i == next_ghost_index:
                    self.ghost_car.x, self.ghost_car.y, self.ghost_car.angle = map(float, row)
                    found = True
                    break
        self.ghost_car.draw(ghost_car_sprite)
        return not found


    def _log_car_properties(self) -> None:
        """Write the car's position and angle to the .csv file."""
        with open(constants.REPLAY_FILE_PATH.format(track_name=self.track.name), "a", newline="") as replay_file:
            csv_writer = csv.writer(replay_file)
            csv_writer.writerow([self.car.x, self.car.y, self.car.angle])


    def _quit(self) -> None:
        """Quits the game."""
        pygame.quit()
        sys.exit()