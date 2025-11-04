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
        pygame.mouse.set_visible(False)
        self.screen: pygame.Surface = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)
        self.game_surface: pygame.Surface = pygame.Surface((constants.WIDTH, constants.HEIGHT))
        self.clock: pygame.time.Clock = pygame.time.Clock()
        pygame.display.set_caption(constants.GAME_TITLE)

        # Track and car
        self.track: Track
        self.personal_best_time: float
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

        # Lap Timers (from old)
        self.lap_start_time: Optional[int] = None
        self.lap_times: list[int] = []
        self.timer_font: pygame.font.Font = pygame.font.Font(constants.TEXT_FONT_PATH, 30)
        self.lap_box: pygame.Rect = pygame.Rect(constants.WIDTH - 320, 20, 260, 250)

        # Sounds
        self.next_lap_sound = pygame.mixer.Sound(
            constants.TRACK_AUDIO_PATH.format(track_name="general", song_type="next_lap"))
        self.next_lap_sound.set_volume(0.5)

        # Fonts
        self.lap_count_font: pygame.font.Font = pygame.font.Font(constants.TEXT_FONT_PATH, 45)
        self.countdown_font: pygame.font.Font = pygame.font.Font(constants.TEXT_FONT_PATH, 120)

        # Text surfaces
        self.lap_count_text: pygame.Surface
        self.lap_count_text_rect: pygame.Rect

    def _scale_mouse_pos(self, pos: tuple[int, int], window_size: tuple[int, int]) -> tuple[int, int]:
        """Scales mouse position from window coordinates to game_surface coordinates."""
        game_surface_size = self.game_surface.get_size()
        if window_size[0] == 0 or window_size[1] == 0:
            return 0, 0
        scale_x = game_surface_size[0] / window_size[0]
        scale_y = game_surface_size[1] / window_size[1]
        return int(pos[0] * scale_x), int(pos[1] * scale_y)

    def _format_time_simple(self, time_ms: int) -> str:
        """Formats time in MM:SS:ms."""
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

    def _update_lap_text(self, is_finished: bool = False) -> None:
        """Generates the lap counter text surface."""
        text: str = "Finish!" if is_finished else f"Lap {self.current_lap} of {constants.NUM_LAPS[self.track.name]}"
        self.lap_count_text = self.lap_count_font.render(text, True, constants.TEXT_COLOR)
        self.lap_count_text_rect = self.lap_count_text.get_rect(center=(constants.WIDTH - 250, constants.HEIGHT - 90))

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
            countdown_rect: pygame.Rect = countdown_surface.get_rect(center=(constants.WIDTH / 2, constants.HEIGHT / 2))
            self.game_surface.blit(countdown_surface, countdown_rect)

    def _display_race_time(self) -> float:
        """Draws the final race time after the race is over."""
        if self.race_start_time is None or self.race_end_time is None:
            return sys.float_info.max  # Should not happen if race_over is True, but good for type safety

        total_time_ms: int = self.race_end_time - self.race_start_time
        total_seconds: float = total_time_ms / 1000
        formatted_time: str = f"{total_seconds:.2f} s"

        time_font: pygame.font.Font = pygame.font.Font(constants.TEXT_FONT_PATH, 60)
        time_surface: pygame.Surface = time_font.render(formatted_time, True, constants.TEXT_COLOR)
        time_rect: pygame.Rect = time_surface.get_rect(center=(constants.WIDTH / 2, constants.HEIGHT / 2))
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

            self.current_lap += 1

            if self.current_lap > constants.NUM_LAPS[self.track.name]:
                self.during_race = False
                self.race_over = True
                self.race_end_time = pygame.time.get_ticks()
                self._update_lap_text(is_finished=True)
                self.lap_start_time = None
            else:
                if self.current_lap == constants.NUM_LAPS[self.track.name]:
                    self._play_next_track()
                else:
                    self.next_lap_sound.play()
                self._update_lap_text()

    def welcome(self) -> None:
        """Displays the title screen and displays the track selection screen when the button is clicked."""
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

            next_action = self.title_screen.handle_events(events, self.screen.get_size())
            if next_action == "exit":
                self._quit()
            elif next_action == "track_selection":
                self.click_sound.play()
                self._track_select()

            self.title_screen.draw()
            self._draw_cursor()

            scaled_surface = pygame.transform.scale(self.game_surface, self.screen.get_size())
            self.screen.blit(scaled_surface, (0, 0))
            pygame.display.flip()
            title_clock.tick(60)

    def _draw_cursor(self) -> None:
        """Draws the custom cursor on the game surface."""
        unscaled_mouse_pos = pygame.mouse.get_pos()
        window_size = self.screen.get_size()
        if window_size[0] == 0 or window_size[1] == 0:
            return

        mouse_pos = self._scale_mouse_pos(unscaled_mouse_pos, window_size)

        if mouse_pos[0] not in [0, constants.WIDTH - 1] and mouse_pos[1] not in [0, constants.HEIGHT - 1]:
            self.game_surface.blit(self.custom_cursor_image, mouse_pos)

    def _track_select(self) -> None:
        """Displays the track selection screen and starts the game a track is selected."""
        self.track_selection = TrackSelection(self.game_surface)
        track_select_clock: pygame.time.Clock = pygame.time.Clock()
        running = True
        while running:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self._quit()
                if event.type == pygame.VIDEORESIZE:
                    self.screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)

            next_action = self.track_selection.handle_events(events, self.screen.get_size())
            if next_action == "exit":
                self._quit()
            elif next_action != "":
                self.click_sound.play()
                self.track = Track(next_action)
                self.car = Car(self.game_surface, self.track.name, is_ghost=False)
                self._run()

            self.track_selection.draw()
            self._draw_cursor()

            scaled_surface = pygame.transform.scale(self.game_surface, self.screen.get_size())
            self.screen.blit(scaled_surface, (0, 0))
            pygame.display.flip()
            track_select_clock.tick(60)

    def _get_personal_best_time(self) -> None:
        """Get the user's personal best time for the current track."""
        personal_best_metadata_path: Path = Path(
            constants.PERSONAL_BEST_METADATA_FILE_PATH.format(track_name=self.track.name))
        best_time: float = float("inf")
        if personal_best_metadata_path.exists():
            with open(personal_best_metadata_path, "r") as personal_best:
                personal_best_data = json.load(personal_best)
            best_time = personal_best_data.get("time", float("inf"))
        self.personal_best_time = best_time

    def _run(self) -> None:
        """The main game loop when the user is racing on a track."""

        # Flags
        found_ghost: bool = False
        running: bool = True
        compared_to_best: bool = False

        # Initialization
        self._get_personal_best_time()
        self._create_replay_file()
        self._update_lap_text()
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
            for event in events:
                if event.type == pygame.QUIT:
                    self._quit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_g:
                        self.show_ghost = not self.show_ghost
                if event.type == pygame.VIDEORESIZE:
                    self.screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)

            if not pygame.mixer.music.get_busy() and not self.race_over:
                self._play_next_track()

            keys: pygame.key.ScancodeWrapper = pygame.key.get_pressed()
            self.car.handle_input(keys, self.during_race)

            max_speed: float = constants.MAX_SPEED
            if self.track.is_off_road(self.car.x, self.car.y):
                max_speed *= 0.5

            self.car.update_position(max_speed)

            self.track.draw(self.game_surface)
            self.game_surface.blit(self.lap_count_text, self.lap_count_text_rect)

            # --- Timer and Lap Box Drawing Logic ---
            if self.race_start_time:
                # 2. Draw Total Timer
                total_time_ms: int
                if self.race_over and self.race_end_time:
                    total_time_ms = self.race_end_time - self.race_start_time
                else:
                    total_time_ms = current_time - self.race_start_time

                time_str: str = f"Total: {self._format_time_simple(total_time_ms)}"
                time_surf: pygame.Surface = self.timer_font.render(time_str, True, constants.TEXT_COLOR)
                time_rect: pygame.Rect = time_surf.get_rect(midtop=(self.lap_box.centerx, self.lap_box.y))
                self.game_surface.blit(time_surf, time_rect)

                # 3. Draw Lap Times Box
                box_y_start: int = time_rect.bottom + 10
                lap_box_main: pygame.Rect = pygame.Rect(self.lap_box.x, box_y_start, self.lap_box.width,
                                                        self.lap_box.height)

                # Draw box background (using semi-transparent surface)
                s: pygame.Surface = pygame.Surface((lap_box_main.width, lap_box_main.height), pygame.SRCALPHA)
                s.fill((30, 30, 30, 180))  # R, G, B, Alpha
                self.game_surface.blit(s, lap_box_main.topleft)
                pygame.draw.rect(self.game_surface, (255, 255, 255), lap_box_main, 2)  # White border

                # Draw title
                title_surf: pygame.Surface = self.timer_font.render("Lap Times", True, (255, 255, 255))
                title_rect: pygame.Rect = title_surf.get_rect(midtop=(lap_box_main.centerx, lap_box_main.y + 10))
                self.game_surface.blit(title_surf, title_rect)

                # Draw lap times
                y_offset: int = title_rect.bottom + 10
                for i, lap_ms in enumerate(self.lap_times):
                    lap_str: str = f"Lap {i + 1}: {self._format_time_simple(lap_ms)}"
                    lap_surf: pygame.Surface = self.timer_font.render(lap_str, True, (220, 220, 220))
                    lap_rect: pygame.Rect = lap_surf.get_rect(topright=(lap_box_main.right - 15, y_offset))

                    if lap_rect.bottom < lap_box_main.bottom - 10:  # Check if it fits
                        self.game_surface.blit(lap_surf, lap_rect)
                        y_offset += 35
            # --- End Timer Logic ---

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
                total_time: float = self._display_race_time()
                if not compared_to_best:
                    self._compare_to_best(total_time)
                    compared_to_best = True
                if not self.applause_played:
                    self.applause_played = True
                    self._play_next_track()
                if not pygame.mixer.music.get_busy():
                    running = False

            self.car.draw(self.car_sprite)

            scaled_surface = pygame.transform.scale(self.game_surface, self.screen.get_size())
            self.screen.blit(scaled_surface, (0, 0))
            pygame.display.flip()

        self._reset_game_state()
        self._track_select()

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
        self.lap_start_time = None
        self.lap_times = []

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

        if total_time < self.personal_best_time:
            metadata = {
                "time": total_time,
                "car_type_index": self.car_type_index
            }
            with open(personal_best_metadata_path, "w") as personal_best:
                json.dump(metadata, personal_best)

            if current_race_file.exists():
                new_personal_best: Path = current_race_file.with_name(constants.PERSONAL_BEST_FILE_NAME)
                current_race_file.rename(new_personal_best)

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