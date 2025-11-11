import csv
import json
from pathlib import Path
from typing import Optional

import pygame

from car import Car
import constants
from track import Track


class Race:

    def __init__(self, game, track_name: str, user_car_type_index: int, ghost_car_type_index: int) -> None:
        """"""
        # General
        self.game = game

        # Track
        self.track_name: str = track_name
        self.track: Track = Track(self.track_name)

        # Pause menu
        self.pause_hover_index: int
        self.is_paused: bool = False
        self.pause_title_font: pygame.font.Font = pygame.font.Font(constants.TEXT_FONT_PATH, 80)
        self.pause_button_font: pygame.font.Font = pygame.font.Font(constants.TEXT_FONT_PATH, 50)
        self.custom_cursor_image: pygame.Surface = pygame.image.load(constants.CURSOR_IMAGE_PATH).convert_alpha()
        self.custom_cursor_image = pygame.transform.scale(self.custom_cursor_image,
                                                          (constants.CURSOR_WIDTH, constants.CURSOR_HEIGHT))
        self.pause_start_time_ms: int = 0
        self.pause_start_time_s: float = 0.0
        self.pause_hover_index: int = 0  # 0=None, 1=Resume, 2=Replay, 3=Exit
        self.pause_title_font: pygame.font.Font = pygame.font.Font(constants.TEXT_FONT_PATH, 80)
        self.pause_button_font: pygame.font.Font = pygame.font.Font(constants.TEXT_FONT_PATH, 50)
        self.pause_overlay: pygame.Surface = pygame.Surface((constants.WIDTH, constants.HEIGHT), pygame.SRCALPHA)
        self.pause_overlay.fill(constants.PAUSE_OVERLAY_COLOR)
        button_x: float = (constants.WIDTH - constants.PAUSE_BUTTON_WIDTH) / 2
        self.resume_button_rect: pygame.Rect = pygame.Rect(button_x, constants.PAUSE_RESUME_Y,
                                                           constants.PAUSE_BUTTON_WIDTH, constants.PAUSE_BUTTON_HEIGHT)
        self.replay_button_rect: pygame.Rect = pygame.Rect(button_x, constants.PAUSE_REPLAY_Y,
                                                           constants.PAUSE_BUTTON_WIDTH, constants.PAUSE_BUTTON_HEIGHT)
        self.exit_button_rect: pygame.Rect = pygame.Rect(button_x, constants.PAUSE_EXIT_Y, constants.PAUSE_BUTTON_WIDTH,
                                                         constants.PAUSE_BUTTON_HEIGHT)

        # Replay
        self.current_race_file: Path = Path(constants.REPLAY_FILE_PATH.format(track_name=self.track.name))

        # Race over menu
        self.race_over_hover_index: int = 0
        race_over_button_x: float = (constants.WIDTH - constants.RACE_OVER_BUTTON_WIDTH) / 2
        self.retry_button_rect: pygame.Rect = pygame.Rect(race_over_button_x, constants.RACE_OVER_RETRY_Y,
                                                          constants.RACE_OVER_BUTTON_WIDTH,
                                                          constants.RACE_OVER_BUTTON_HEIGHT)
        self.exit_race_over_button_rect: pygame.Rect = pygame.Rect(race_over_button_x, constants.RACE_OVER_EXIT_Y,
                                                                   constants.RACE_OVER_BUTTON_WIDTH,
                                                                   constants.RACE_OVER_BUTTON_HEIGHT)

        # Lap Timers
        self.lap_start_time: Optional[int] = None
        self.lap_times: list[int] = []
        self.fastest_lap_in_race: Optional[int] = None
        self.timer_font: pygame.font.Font = pygame.font.Font(constants.FALLBACK_FONT_PATH, 30)
        self.timer_font.set_bold(True)

        # Sound and Music
        self.next_lap_sound: Sound = pygame.mixer.Sound(constants.TRACK_AUDIO_PATH.format(track_name="general", song_type="next_lap"))
        self.next_lap_sound.set_volume(0.5)

        # User Car
        self.user_car_type_index: int = user_car_type_index
        self.user_car: Car = Car(self.game.game_surface, self.track_name, False, self.user_car_type_index)
        self.max_speed: float = constants.MAX_SPEED

        # User Data
        self.personal_best_time: float = float("inf")
        self.fastest_lap_record: float = float("inf")

        # Ghost Car
        self.ghost_car_type_index: int = ghost_car_type_index
        self.ghost_car = Car(self.game.game_surface, self.track.name, True, self.ghost_car_type_index)
        self.ghost_filename = constants.PERSONAL_BEST_FILE_PATH.format(track_name=self.track.name)
        self.next_ghost_index: int = 1
        self.show_ghost: bool = True
        self.ghost_found: bool = False
        self.ghost_done: bool = False

        # Time
        self.countdown_start_time: int
        self.elapsed_race_time_ms: int = 0
        self.elapsed_race_time_s: float = 0.0
        self.current_time: int

        # Race state
        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.running: bool = True
        self.compared_to_best: bool = False
        self.current_lap: int = 1
        self.has_checkpoint: bool = False
        self.countdown_done: bool = False
        self.during_race: bool = False
        self.race_over: bool = False
        self.applause_played: bool = False
        self.current_track_index: int = 0
        self.race_start_time_ms: int = 0
        self.race_end_time_ms: int = 0
        self.countdown_start_time: int = 0

        # Fonts
        self.countdown_font: pygame.font.Font = pygame.font.Font(constants.TEXT_FONT_PATH, 120)

    def _get_current_time(self):
        """Get the current time since the program started in ms"""
        self.current_time = pygame.time.get_ticks()

    def _next_frame(self):
        """Establish a frame rate of 60 FPS"""
        self.clock.tick(60)

    def _get_max_speed(self):
        """Get the maximum speed of the car based on the constants and the car's off-road status"""
        self.max_speed = constants.MAX_SPEED
        if self.track.is_off_road(self.user_car.x, self.user_car.y):
            self.max_speed *= 0.5

    def start(self) -> bool:
        """The main game loop when the user is racing on a track"""
        self._initialize_race()
        while self.running:
            self._next_frame()
            self._get_current_time()
            self._get_elapsed_race_time()
            self.game.get_scaled_mouse_pos()
            self._handle_race_events()
            if not pygame.mixer.music.get_busy() and not self.race_over and not self.is_paused:
                self._play_next_track()
            if self.is_paused:
                match self._pause():
                    case "replay":
                        self._clean_up()
                        return True
                    case "exit_to_menu":
                        self._clean_up()
                        return False
                    case "resume":
                        self._unpause()
            elif self.during_race:
                self.user_car.handle_input(pygame.key.get_pressed(), self.during_race)
                self._get_max_speed()
                self.user_car.update_position(self.max_speed)
                self._check_lap_completion()
                if self.elapsed_race_time_ms < self.personal_best_time:
                    self._log_car_properties()
            elif self.race_over:
                self.user_car.handle_input(pygame.key.get_pressed(), self.during_race)
                self._get_max_speed()
                self.user_car.update_position(self.max_speed)
                if not self.compared_to_best:
                    self._display_race_time()
                    self._compare_to_best()
                    self.compared_to_best = True
                if not self.applause_played:
                    self.applause_played = True
                    self._play_next_track()
                match self._handle_race_over_menu():
                    case "replay":
                        self._clean_up()
                        return True
                    case "exit_to_menu":
                        self._clean_up()
                        return False
            self._draw_race()
        pygame.mixer.music.stop()
        pygame.mixer.music.load(constants.GENERAL_AUDIO_PATH.format(song_name="intro"))
        pygame.mixer.music.play(-1)
        return False

    def _clean_up(self):
        """Performs clean up actions before exiting the race"""
        if self.current_race_file.exists():
            self.current_race_file.unlink()
        pygame.mixer.music.stop()

    def _get_elapsed_race_time(self):
        """Gets the """
        if self.during_race and not self.is_paused:
            self.elapsed_race_time_ms = self.current_time - self.race_start_time_ms
        elif self.during_race and self.is_paused:
            self.elapsed_race_time_ms = self.pause_start_time_ms - self.race_start_time_ms
        self.elapsed_race_time_s = self.elapsed_race_time_ms / 1000.0
        

    def _draw_race(self) -> None:
        """Draws all the visual elements for the race"""

        # Calculate camera offset to center car
        self.camera_x = self.user_car.x - (constants.WIDTH / 2)
        self.camera_y = self.user_car.y - (constants.HEIGHT / 2)

        # Fill the screen with the track's ground color
        # Temporary until the maps are drawn bigger to have more detail past edges
        self.game.game_surface.fill(constants.TRACK_FILL_COLORS[self.track.name])

        # Pass camera offset to track drawing
        self.track.draw(self.game.game_surface, self.camera_x, self.camera_y)

        # Draw ghost
        if self.ghost_found and self.show_ghost and not self.ghost_done:
            self._draw_ghost(self.camera_x, self.camera_y)
        if self.during_race and not self.is_paused:
            self.next_ghost_index += 1

        # Draw car
        self.user_car.draw(self.camera_x, self.camera_y)

        # Overlays
        if not self.race_over:
            self._draw_race_ui()
        if self.is_paused:
            self._draw_pause_menu()
        else:
            if not self.countdown_done:
                self._draw_countdown()

        # Draw the race over menu if the race is over (and not paused)
        if self.race_over and not self.is_paused:
            self._draw_race_over_menu()
            self._display_race_time()

        # Only draw the cursor if we are in a menu
        if self.is_paused or self.race_over:
            self.game.draw_cursor()

        # Draw the letterboxed game_surface to the screen
        self.game.draw_letterboxed_surface()
        pygame.display.flip()

    def _draw_pause_menu(self) -> None:
        # Draws the pause menu overlay and buttons onto the game_surface
        # Draw the semi-transparent overlay
        self.game.game_surface.blit(self.pause_overlay, (0, 0))

        # Draw Title
        title_text = self.pause_title_font.render("Paused", True, constants.PAUSE_TITLE_COLOR)
        title_rect = title_text.get_rect(center=(constants.WIDTH / 2, constants.PAUSE_TITLE_Y))
        self.game.game_surface.blit(title_text, title_rect)

        # Determine button colors based on hover
        resume_color = constants.PAUSE_BUTTON_HOVER_COLOR if self.pause_hover_index == 1 else constants.PAUSE_BUTTON_COLOR
        replay_color = constants.PAUSE_BUTTON_HOVER_COLOR if self.pause_hover_index == 2 else constants.PAUSE_BUTTON_COLOR
        exit_color = constants.PAUSE_BUTTON_HOVER_COLOR if self.pause_hover_index == 3 else constants.PAUSE_BUTTON_COLOR

        # Create and draw button text
        resume_text = self.pause_button_font.render("Resume", True, resume_color)
        replay_text = self.pause_button_font.render("Replay", True, replay_color)
        exit_text = self.pause_button_font.render("Exit to Menu", True, exit_color)

        self.game.game_surface.blit(resume_text, resume_text.get_rect(center=self.resume_button_rect.center))
        self.game.game_surface.blit(replay_text, replay_text.get_rect(center=self.replay_button_rect.center))
        self.game.game_surface.blit(exit_text, exit_text.get_rect(center=self.exit_button_rect.center))

    def _draw_race_ui(self) -> None:
        """Draws the main race UI elements (lap, times) onto the game surface"""

        # Lap counter
        lap_str = "Finish!" if self.race_over else f"Lap {self.current_lap}/{constants.NUM_LAPS[self.track.name]}"
        lap_surf = self.timer_font.render(lap_str, True, constants.TEXT_COLOR)

        # Total Time
        total_time_str = self._format_time_simple()
        total_time_surf = self.timer_font.render(total_time_str, True, constants.TEXT_COLOR)

        # Blit
        self.game.game_surface.blit(lap_surf, (20, 10))
        self.game.game_surface.blit(total_time_surf, (20, 50))

    def _initialize_pause(self) -> None:
        pygame.mixer_music.pause()
        self.game.click_sound.play()
        self.pause_start_time_ms = pygame.time.get_ticks()
        self.pause_start_time_s = self.pause_start_time_ms / 1000.0
        self.pause_hover_index = 0

    def _unpause(self):
        pygame.mixer.music.unpause()
        pause_duration = pygame.time.get_ticks() - self.pause_start_time_ms
        self.countdown_start_time += pause_duration
        if self.race_start_time_ms is not None:
            self.race_start_time_ms += pause_duration

    def _handle_race_events(self) -> None:
        """Handles key and button presses"""
        self.events = pygame.event.get()
        for event in self.events:
            if event.type == pygame.QUIT:
                self._clean_up()
                self.game.quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if not self.race_over:
                        self.is_paused = not self.is_paused
                        if self.is_paused:
                            self._initialize_pause()
                        else:
                            self._unpause()
                if event.key == pygame.K_g:
                    self.show_ghost = not self.show_ghost
            if event.type == pygame.VIDEORESIZE:
                self.game.screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)

    def _initialize_race(self) -> None:
        """Perform initial actions before the race begins"""
        self._get_personal_best_time()
        self._create_replay_file()
        if self.show_ghost:
            self.ghost_found = self._get_ghost_info()
        self.countdown_start_time = pygame.time.get_ticks()
        self._play_next_track()

    def _get_personal_best_time(self) -> None:
        """Get the user's personal best time for the current track"""
        personal_best_metadata_path: Path = Path(constants.PERSONAL_BEST_METADATA_FILE_PATH.format(track_name=self.track.name))
        self.personal_best_time = float("inf")
        if personal_best_metadata_path.exists():
            with open(personal_best_metadata_path, "r") as file:
                personal_best_data = json.load(file)
            self.personal_best_time = personal_best_data.get("time", float("inf"))

    def _create_replay_file(self) -> None:
        """Creates a new .csv file when the race begins to log the user's car position"""
        with open(constants.REPLAY_FILE_PATH.format(track_name=self.track.name), "w", newline=""):
            pass

    def _get_ghost_info(self) -> bool:
        """Returns True if the info for the ghost exists and False otherwise"""
        return Path(self.ghost_filename).exists()

    def _play_next_track(self) -> None:
        """Loads and plays the next audio track in the playlist"""
        if self.current_track_index < len(self.track.playlist):
            track_path, loops = self.track.playlist[self.current_track_index]
            pygame.mixer.music.load(track_path)
            pygame.mixer.music.play(loops)
            self.current_track_index += 1

    def _pause(self) -> str:
        """Handles input for the pause menu"""
        if self.resume_button_rect.collidepoint(self.game.scaled_mouse_pos):
            self.pause_hover_index = 1
        elif self.replay_button_rect.collidepoint(self.game.scaled_mouse_pos):
            self.pause_hover_index = 2
        elif self.exit_button_rect.collidepoint(self.game.scaled_mouse_pos):
            self.pause_hover_index = 3
        else:
            self.pause_hover_index = 0

        for event in self.events:
            if event.type == pygame.QUIT:
                self.game.quit()

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if self.pause_hover_index == 1:
                    self.game.click_sound.play()
                    self.is_paused = False
                    return "resume"
                elif self.pause_hover_index == 2:
                    self.game.click_sound.play()
                    return "replay"
                elif self.pause_hover_index == 3:
                    self.game.click_sound.play()
                    return "exit_to_menu"
        return ""

    def _display_race_time(self):
        """Draws the final race time after the race is over"""
        formatted_time: str = f"{self.elapsed_race_time_s:.2f} s"

        time_font: pygame.font.Font = pygame.font.Font(constants.TEXT_FONT_PATH, 60)
        time_surface: pygame.Surface = time_font.render(formatted_time, True, constants.TEXT_COLOR)
        time_rect: pygame.Rect = time_surface.get_rect(center=(constants.WIDTH / 2, 325))
        self.game.game_surface.blit(time_surface, time_rect)

    def _check_lap_completion(self) -> None:
        """Checks for checkpoint and finish line crosses and updates lap count"""
        if self.track.check_checkpoint(self.user_car.x, self.user_car.y):
            self.has_checkpoint = True
        if self.has_checkpoint and self.track.check_finish_line(self.user_car.x, self.user_car.y):
            self.has_checkpoint = False
            self.current_lap += 1
            if self.current_lap > constants.NUM_LAPS[self.track.name]:
                self.during_race = False
                self.race_over = True
                self.race_end_time_ms = pygame.time.get_ticks()
                self.lap_start_time = None
            else:
                if self.current_lap == constants.NUM_LAPS[self.track.name]:
                    self._play_next_track()
                else:
                    self.next_lap_sound.play()

    def _draw_countdown(self) -> None:
        """Calculates and draws the pre-race countdown timer"""
        elapsed: int = self.current_time - self.countdown_start_time
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
                self.race_start_time_ms = pygame.time.get_ticks()
                self.lap_start_time = self.race_start_time_ms
            countdown_text = "Go!"
        else:
            self.countdown_done = True
        if countdown_text:
            countdown_surface: pygame.Surface = self.countdown_font.render(countdown_text, True, constants.TEXT_COLOR)
            countdown_rect: pygame.Rect = countdown_surface.get_rect(center=(constants.WIDTH / 2, constants.HEIGHT / 2))
            self.game.game_surface.blit(countdown_surface, countdown_rect)

    def _compare_to_best(self) -> None:
        """Compare the current time to the personal best, and if it was beaten, replace the personal best"""
        personal_best_metadata_path: Path = Path(constants.PERSONAL_BEST_METADATA_FILE_PATH.format(track_name=self.track.name))
        if self.elapsed_race_time_s < self.personal_best_time:
            metadata = {
                "time": self.elapsed_race_time_s,
                "car_type_index": self.user_car_type_index
            }
            with open(personal_best_metadata_path, "w") as file:
                json.dump(metadata, file)
            if self.current_race_file.exists():
                new_personal_best: Path = self.current_race_file.with_name(constants.PERSONAL_BEST_FILE_NAME)
                self.current_race_file.replace(new_personal_best)
            self.personal_best_time = self.elapsed_race_time_s
        if self.current_race_file.exists():
            self.current_race_file.unlink()

    def _handle_race_over_menu(self) -> str:
        """Handles input for the race over menu"""
        if self.retry_button_rect.collidepoint(self.game.scaled_mouse_pos):
            self.race_over_hover_index = 1
        elif self.exit_race_over_button_rect.collidepoint(self.game.scaled_mouse_pos):
            self.race_over_hover_index = 2
        else:
            self.race_over_hover_index = 0
        for event in self.events:
            if event.type == pygame.QUIT:
                self.game.quit()
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if self.race_over_hover_index == 1:
                    self.game.click_sound.play()
                    return "replay"
                elif self.race_over_hover_index == 2:
                    self.game.click_sound.play()
                    return "exit_to_menu"
        return ""

    def _draw_ghost(self, camera_x: float, camera_y: float):
        """Retrieves the ghost's position at this frame and draws it on the screen, returning False if the ghost has finished the race"""
        try:
            found: bool = False
            with open(self.ghost_filename, newline="") as file:
                reader = csv.reader(file)
                for i, row in enumerate(reader):
                    if i == self.next_ghost_index:
                        self.ghost_car.x, self.ghost_car.y, self.ghost_car.angle = map(float, row)
                        self.ghost_car.draw(camera_x, camera_y)
                        found = True
                        break
            self.ghost_done = not found
        except FileNotFoundError:
            self.ghost_found = False
        except Exception:
            self.ghost_found = False

    def _log_car_properties(self) -> None:
        """Write the car's position and angle to the .csv file"""
        with open(constants.REPLAY_FILE_PATH.format(track_name=self.track.name), "a", newline="") as replay_file:
            csv_writer = csv.writer(replay_file)
            csv_writer.writerow([self.user_car.x, self.user_car.y, self.user_car.angle])

    def _format_time_simple(self) -> str:
        """Formats time in MM:SS:ms"""
        minutes: int = int(self.elapsed_race_time_s // 60)
        seconds: int = int(self.elapsed_race_time_s % 60)
        milliseconds: int = int((self.elapsed_race_time_ms % 1000) // 10)
        return f"{minutes:02}:{seconds:02}:{milliseconds:02}"

    def _draw_race_over_menu(self) -> None:
        """Draws the race over menu buttons onto the game_surface"""

        # Draw Title
        title_text = self.pause_title_font.render("Race Finished!", True, constants.RACE_OVER_TITLE_COLOR)
        title_rect = title_text.get_rect(center=(constants.WIDTH / 2, constants.RACE_OVER_TITLE_Y))
        self.game.game_surface.blit(title_text, title_rect)

        # Determine button colors based on hover
        retry_color = constants.RACE_OVER_BUTTON_HOVER_COLOR if self.race_over_hover_index == 1 else constants.RACE_OVER_BUTTON_COLOR
        exit_color = constants.RACE_OVER_BUTTON_HOVER_COLOR if self.race_over_hover_index == 2 else constants.RACE_OVER_BUTTON_COLOR

        # Create and draw button text
        retry_text = self.pause_button_font.render("Retry", True, retry_color)
        exit_text = self.pause_button_font.render("Exit to Menu", True, exit_color)

        self.game.game_surface.blit(retry_text, retry_text.get_rect(center=self.retry_button_rect.center))
        self.game.game_surface.blit(exit_text, exit_text.get_rect(center=self.exit_race_over_button_rect.center))