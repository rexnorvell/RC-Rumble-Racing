import csv
import json
import os
import shutil
from pathlib import Path
from typing import Optional

import pygame

from car import Car
import constants
from track import Track


class Race:

    def __init__(self, game, track_name: str, car_index: int, style_index: int, difficulty: str, save_manager) -> None:
        # General
        self.game = game
        self.save_manager = save_manager
        self.difficulty = difficulty

        # Track
        self.track_name: str = track_name
        self.track: Track = Track(self.track_name)

        # Pause menu
        self.pause_hover_index: int
        self.is_paused: bool = False
        self.pause_start_time_ms: int = 0
        self.pause_start_time_s: float = 0.0
        self.pause_hover_index: int = 0  # 0=None, 1=Resume, 2=Replay, 3=Exit
        self.dark_overlay: pygame.Surface = pygame.Surface((constants.WIDTH, constants.HEIGHT), pygame.SRCALPHA)
        self.dark_overlay.fill((0, 0, 0, constants.PAUSE_OVERLAY_OPACITY))
        button_x: float = (constants.WIDTH - constants.PAUSE_BUTTON_WIDTH) / 2
        self.resume_button_rect: pygame.Rect = pygame.Rect(button_x, constants.PAUSE_RESUME_Y,
                                                           constants.PAUSE_BUTTON_WIDTH, constants.PAUSE_BUTTON_HEIGHT)
        self.replay_button_rect: pygame.Rect = pygame.Rect(button_x, constants.PAUSE_REPLAY_Y,
                                                           constants.PAUSE_BUTTON_WIDTH, constants.PAUSE_BUTTON_HEIGHT)
        self.exit_button_rect: pygame.Rect = pygame.Rect(button_x, constants.PAUSE_EXIT_Y, constants.PAUSE_BUTTON_WIDTH,
                                                         constants.PAUSE_BUTTON_HEIGHT)
        self.pause_image_left: pygame.Surface = pygame.image.load(
            constants.PAUSE_MENU_IMAGE_PATH.format(image_name="left")).convert_alpha()
        self.pause_image_left = pygame.transform.scale(self.pause_image_left, (constants.WIDTH, constants.HEIGHT))
        self.pause_default_image_right: pygame.Surface = pygame.image.load(
            constants.PAUSE_MENU_IMAGE_PATH.format(image_name="right")).convert_alpha()
        self.pause_default_image_right = pygame.transform.scale(self.pause_default_image_right,
                                                                (constants.WIDTH, constants.HEIGHT))
        self.pause_image_hover_1: pygame.Surface = pygame.image.load(
            constants.PAUSE_MENU_IMAGE_PATH.format(image_name="1")).convert_alpha()
        self.pause_image_hover_1 = pygame.transform.scale(self.pause_image_hover_1, (constants.WIDTH, constants.HEIGHT))
        self.pause_image_hover_2: pygame.Surface = pygame.image.load(
            constants.PAUSE_MENU_IMAGE_PATH.format(image_name="2")).convert_alpha()
        self.pause_image_hover_2 = pygame.transform.scale(self.pause_image_hover_2, (constants.WIDTH, constants.HEIGHT))
        self.pause_image_hover_3: pygame.Surface = pygame.image.load(
            constants.PAUSE_MENU_IMAGE_PATH.format(image_name="3")).convert_alpha()
        self.pause_image_hover_3 = pygame.transform.scale(self.pause_image_hover_3, (constants.WIDTH, constants.HEIGHT))
        self.pause_image_right: pygame.Surface = self.pause_default_image_right

        # Replay
        self.current_race_file: Path = Path(constants.REPLAY_FILE_PATH.format(track_name=self.track.name))

        # Race Over Menu
        self.race_over_hover_index: int = 0
        race_over_button_x: float = (constants.WIDTH - constants.RACE_OVER_BUTTON_WIDTH) / 2
        self.retry_button_rect: pygame.Rect = pygame.Rect(race_over_button_x, constants.RACE_OVER_RETRY_Y,
                                                          constants.RACE_OVER_BUTTON_WIDTH,
                                                          constants.RACE_OVER_BUTTON_HEIGHT)
        self.exit_race_over_button_rect: pygame.Rect = pygame.Rect(race_over_button_x, constants.RACE_OVER_EXIT_Y,
                                                                   constants.RACE_OVER_BUTTON_WIDTH,
                                                                   constants.RACE_OVER_BUTTON_HEIGHT)
        self.race_over_image_left: pygame.Surface = pygame.image.load(
            constants.RACE_OVER_IMAGE_PATH.format(image_name="left")).convert_alpha()
        self.race_over_image_left = pygame.transform.scale(self.race_over_image_left,
                                                           (constants.WIDTH, constants.HEIGHT))
        self.race_over_default_image_right: pygame.Surface = pygame.image.load(
            constants.RACE_OVER_IMAGE_PATH.format(image_name="right")).convert_alpha()
        self.race_over_default_image_right = pygame.transform.scale(self.race_over_default_image_right,
                                                                    (constants.WIDTH, constants.HEIGHT))
        self.race_over_image_hover_1: pygame.Surface = pygame.image.load(
            constants.RACE_OVER_IMAGE_PATH.format(image_name="1")).convert_alpha()
        self.race_over_image_hover_1 = pygame.transform.scale(self.race_over_image_hover_1,
                                                              (constants.WIDTH, constants.HEIGHT))
        self.race_over_image_hover_2: pygame.Surface = pygame.image.load(
            constants.RACE_OVER_IMAGE_PATH.format(image_name="2")).convert_alpha()
        self.race_over_image_hover_2 = pygame.transform.scale(self.race_over_image_hover_2,
                                                              (constants.WIDTH, constants.HEIGHT))
        self.race_over_image_right: pygame.Surface = self.race_over_default_image_right
        self.formatted_time: str
        self.time_font: pygame.font.Font = pygame.font.Font(constants.TEXT_FONT_PATH, 60)
        self.time_surface: pygame.Surface
        self.time_rect: pygame.Rect
        self.time_shadow_surface: pygame.Surface
        self.time_shadow_rect: pygame.Rect

        # Lap Timers
        self.timer_font: pygame.font.Font = pygame.font.Font(constants.FALLBACK_FONT_PATH, 30)
        self.timer_font.set_bold(True)

        # Sound and Music
        self.next_lap_sound: pygame.mixer.Sound = pygame.mixer.Sound(
            constants.TRACK_AUDIO_PATH.format(track_name="general", song_type="next_lap"))
        self.next_lap_sound.set_volume(0.5)
        self.respawn_sound: pygame.mixer.Sound = pygame.mixer.Sound(
            constants.TRACK_AUDIO_PATH.format(track_name="general", song_type="respawn"))
        self.respawn_sound.set_volume(0.5)

        # User Car
        self.user_car_index = car_index
        self.user_style_index = style_index
        self.user_car_config = constants.CAR_DEFINITIONS[self.user_car_index]

        self.user_car: Car = Car(self.game.game_surface, self.track.name, False, self.user_car_config,
                                 self.user_style_index)

        # User Data
        self.personal_best_time: float = float("inf")

        # Ghost Car
        # Use the separate ghost definition from constants
        self.ghost_car_config = constants.GHOST_CAR_DEFINITION
        self.ghost_car = Car(self.game.game_surface, self.track.name, True, self.ghost_car_config, 0)

        # Determine Ghost File based on difficulty
        if self.difficulty == constants.GHOST_DIFFICULTY_PERSONAL_BEST:
            self.ghost_filename = constants.PERSONAL_BEST_FILE_PATH.format(track_name=self.track.name)
            self.ghost_metadata_path = constants.PERSONAL_BEST_METADATA_FILE_PATH.format(track_name=self.track.name)
        else:
            self.ghost_filename = constants.GHOST_FILE_PATH.format(track_name=self.track.name,
                                                                   difficulty=self.difficulty)
            self.ghost_metadata_path = constants.GHOST_METADATA_FILE_PATH.format(track_name=self.track.name,
                                                                                 difficulty=self.difficulty)

        self.next_ghost_index: int = 1
        self.show_ghost: bool = True
        self.ghost_found: bool = False
        self.ghost_done: bool = False
        self.ghost_total_time: float = float("inf")

        # Time
        self.countdown_start_time: int
        self.elapsed_race_time_ms: int = 0
        self.elapsed_race_time_s: float = 0.0
        self.current_time: int

        # Race State
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

        # UI Elements
        self.lap_str: str
        self.lap_surf: pygame.Surface
        self.lap_shadow: pygame.Surface

        # Fonts
        self.countdown_font: pygame.font.Font = pygame.font.Font(constants.TEXT_FONT_PATH, 120)

    def _get_current_time(self):
        """Get the current time since the program started in ms"""
        self.current_time = pygame.time.get_ticks()

    def _next_frame(self):
        """Establish a frame rate of 60 FPS"""
        self.clock.tick(60)

    def _set_max_speed(self):
        """Set the maximum speed of the car based on the constants and the car's off-road status"""
        self.user_car.is_off_road = True if self.track.is_off_road(self.user_car.x, self.user_car.y) else False
        self.user_car.set_max_speed()

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
                self._set_max_speed()
                self.user_car.handle_input(pygame.key.get_pressed(), self.during_race)
                self.user_car.update_position()
                self._check_out_of_bounds()
                self._check_lap_completion()
                if self.elapsed_race_time_s < (self.personal_best_time + 1):
                    self.user_car.log_properties(self.track_name)
            elif self.race_over:
                self._set_max_speed()
                self.user_car.handle_input(pygame.key.get_pressed(), self.during_race)
                self.user_car.update_position()
                if not self.compared_to_best:
                    self._compare_to_best()
                    self._check_unlocks()  # Check for progression
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

        # Pass camera offset to track drawing
        self.track.draw(self.game.game_surface, self.camera_x, self.camera_y)

        # Draw ghost
        if self.ghost_found and not self.ghost_done and not self.race_over:
            if self.show_ghost:
                self._draw_ghost()
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

        # Only draw the cursor if we are in a menu
        if self.is_paused or self.race_over:
            self.game.draw_cursor()

        # Draw the letterboxed game_surface to the screen
        self.game.draw_letterboxed_surface()
        pygame.display.flip()

    def _draw_pause_menu(self) -> None:
        """Draws the pause menu overlay and buttons onto the game_surface"""

        # Control transition
        current_time: int = pygame.time.get_ticks()
        time_elapsed_ms: int = current_time - self.pause_start_time_ms
        transition_duration_ms: int = 250
        percent_progress: float = min(time_elapsed_ms, transition_duration_ms) / transition_duration_ms

        # Adjust the semi-transparent overlay
        dark_overlay_opacity: int = int(percent_progress * constants.PAUSE_OVERLAY_OPACITY)
        dark_overlay_color: tuple[int, int, int, int] = (0, 0, 0, dark_overlay_opacity)
        self.dark_overlay.fill(dark_overlay_color)

        # Calculate the x coordinates of the left and right images for the pause menu
        left_image_x: int = int(percent_progress * constants.WIDTH) - constants.WIDTH
        right_image_x: int = constants.WIDTH - int(percent_progress * constants.WIDTH)

        # Blit everything to the game surface
        self.game.game_surface.blit(self.dark_overlay, (0, 0))
        self.game.game_surface.blit(self.pause_image_left, (left_image_x, 0))
        self.game.game_surface.blit(self.pause_image_right, (right_image_x, 0))

    def _draw_race_ui(self) -> None:
        """Draws the main race UI elements (lap, times) onto the game surface"""

        # Total Time
        total_time_str: str = self._format_time_simple()
        total_time_surf: pygame.Surface = self.timer_font.render(total_time_str, True, constants.TEXT_COLOR)
        total_time_shadow: pygame.Surface = self.timer_font.render(total_time_str, True, constants.TEXT_SHADOW_COLOR)

        # Blit
        self.game.game_surface.blit(self.lap_shadow, (22, 12))
        self.game.game_surface.blit(self.lap_surf, (20, 10))
        self.game.game_surface.blit(total_time_shadow, (22, 52))
        self.game.game_surface.blit(total_time_surf, (20, 50))

    def _initialize_pause(self) -> None:
        """Perform one-time operations upon pausing the race"""
        pygame.mixer.music.pause()
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
            if self.ghost_found:
                self._calculate_ghost_time()
        self._render_lap_text()
        self.user_car.set_respawn_point(self.user_car.start_x, self.user_car.start_y, self.user_car.start_angle)
        self.countdown_start_time = pygame.time.get_ticks()
        self._play_next_track()

    def _get_personal_best_time(self) -> None:
        """Get the user's personal best time for the current track"""
        personal_best_metadata_path: Path = Path(
            constants.PERSONAL_BEST_METADATA_FILE_PATH.format(track_name=self.track.name))
        self.personal_best_time = float("inf")
        if personal_best_metadata_path.exists():
            try:
                with open(personal_best_metadata_path, "r") as file:
                    personal_best_data = json.load(file)
                self.personal_best_time = personal_best_data.get("time", float("inf"))
            except (json.JSONDecodeError, IOError):
                print("Error loading personal best metadata")

    def _create_replay_file(self) -> None:
        """Creates a new .csv file when the race begins to log the user's car position"""
        with open(constants.REPLAY_FILE_PATH.format(track_name=self.track.name), "w", newline=""):
            pass

    def _get_ghost_info(self) -> bool:
        """Returns True if the info for the ghost exists and False otherwise"""
        return Path(self.ghost_filename).exists()

    def _calculate_ghost_time(self):
        """Estimates ghost finish time, preferring JSON metadata if available"""
        # Try loading JSON first
        meta_path = Path(self.ghost_metadata_path)
        if meta_path.exists():
            try:
                with open(meta_path, 'r') as f:
                    data = json.load(f)
                    self.ghost_total_time = data.get("time", float("inf"))
                    return  # Success
            except Exception:
                pass  # Fallback to CSV method

        # Fallback: Count CSV lines
        try:
            with open(self.ghost_filename, "r") as f:
                row_count = sum(1 for _ in f)
            # 60 FPS recording rate
            self.ghost_total_time = row_count / 60.0
        except Exception:
            self.ghost_total_time = float("inf")

    def _check_unlocks(self):
        """Unlocks next track if Medium Ghost is beaten"""
        if self.difficulty == "medium":
            # If player time is less than ghost time, player won
            if self.elapsed_race_time_s < self.ghost_total_time:
                next_track = self.save_manager.get_next_track_name(self.track_name)
                if next_track:
                    print(f"Beat Medium Ghost! Unlocking {next_track}")
                    self.save_manager.unlock_track(next_track)

    def _play_next_track(self) -> None:
        """Loads and plays the next audio track in the playlist"""
        if self.current_track_index < len(self.track.playlist):
            track_path, loops = self.track.playlist[self.current_track_index]
            pygame.mixer.music.load(track_path)
            pygame.mixer.music.play(loops)
            self.current_track_index += 1

    def _pause(self) -> str:
        """Handles input for the pause menu"""
        previous_index: int = self.pause_hover_index
        if self.resume_button_rect.collidepoint(self.game.scaled_mouse_pos):
            self.pause_image_right = self.pause_image_hover_1
            self.pause_hover_index = 1
        elif self.replay_button_rect.collidepoint(self.game.scaled_mouse_pos):
            self.pause_image_right = self.pause_image_hover_2
            self.pause_hover_index = 2
        elif self.exit_button_rect.collidepoint(self.game.scaled_mouse_pos):
            self.pause_image_right = self.pause_image_hover_3
            self.pause_hover_index = 3
        else:
            self.pause_image_right = self.pause_default_image_right
            self.pause_hover_index = 0
        if previous_index != self.pause_hover_index and self.pause_hover_index != 0:
            self.game.hover_sound.play()
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

    def _check_out_of_bounds(self) -> None:
        """Checks if the car is outside the hard map limits and respawns it."""
        if self.track.is_out_of_bounds(self.user_car.x, self.user_car.y):
            self.respawn_sound.play()
            self.user_car.respawn()

    def _check_lap_completion(self) -> None:
        """Checks for checkpoint and finish line crosses and updates lap count"""

        # Check for checkpoint FIRST
        if self.track.check_checkpoint(self.user_car.x, self.user_car.y):
            if not self.has_checkpoint:
                self.has_checkpoint = True
                # Update the car's respawn point to this checkpoint
                cp_x = self.track.checkpoint_1.centerx
                cp_y = self.track.checkpoint_1.centery
                cp_angle = constants.CHECKPOINT_ANGLES[self.track.name]
                self.user_car.set_respawn_point(cp_x, cp_y, cp_angle)

        # Check for finish line
        if self.has_checkpoint and self.track.check_finish_line(self.user_car.x, self.user_car.y):
            self.has_checkpoint = False
            self.current_lap += 1
            self._render_lap_text()

            # Reset respawn point to the start line for the new lap
            start_x = self.user_car.start_x
            start_y = self.user_car.start_y
            start_angle = self.user_car.start_angle
            self.user_car.set_respawn_point(start_x, start_y, start_angle)

            # Check if race is over
            if self.current_lap > constants.NUM_LAPS[self.track.name]:
                self.during_race = False
                self.race_over = True
                self.race_end_time_ms = pygame.time.get_ticks()
                self._render_final_time()
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
            countdown_text = "Go!"
        else:
            self.countdown_done = True
        if countdown_text:
            countdown_surface: pygame.Surface = self.countdown_font.render(countdown_text, True, constants.TEXT_COLOR)
            countdown_rect: pygame.Rect = countdown_surface.get_rect(center=(constants.WIDTH / 2, constants.HEIGHT / 2))
            self.game.game_surface.blit(countdown_surface, countdown_rect)

    def _render_lap_text(self):
        """Renders the lap text whenever the user reaches a new lap"""
        self.lap_str: str = f"Lap {self.current_lap}/{constants.NUM_LAPS[self.track.name]}"
        self.lap_surf: pygame.Surface = self.timer_font.render(self.lap_str, True, constants.TEXT_COLOR)
        self.lap_shadow: pygame.Surface = self.timer_font.render(self.lap_str, True, constants.TEXT_SHADOW_COLOR)

    def _render_final_time(self):
        """Renders the final time when the user reaches finishes the race"""
        self.formatted_time = f"{self.elapsed_race_time_s:.2f} s"
        self.time_surface: pygame.Surface = self.time_font.render(self.formatted_time, True, constants.TEXT_COLOR)
        self.time_rect: pygame.Rect = self.time_surface.get_rect(center=(constants.WIDTH / 2, 325))
        self.time_shadow_surface: pygame.Surface = self.time_font.render(self.formatted_time, True,
                                                                         constants.TEXT_SHADOW_COLOR)
        self.time_shadow_rect: pygame.Rect = self.time_shadow_surface.get_rect(
            center=(constants.WIDTH / 2 + 4, 325 + 4))

    def _compare_to_best(self) -> None:
        """Compare the current time to the personal best, and if it was beaten, replace the personal best"""
        self.compared_to_best = True
        if self.elapsed_race_time_s < self.personal_best_time:
            personal_best_metadata_path: Path = Path(
                constants.PERSONAL_BEST_METADATA_FILE_PATH.format(track_name=self.track.name))
            metadata = {
                "time": self.elapsed_race_time_s,
                "car_type_index": self.user_car_index,
                "style_index": self.user_style_index
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
        previous_index: int = self.race_over_hover_index
        if self.retry_button_rect.collidepoint(self.game.scaled_mouse_pos):
            self.race_over_image_right = self.race_over_image_hover_1
            self.race_over_hover_index = 1
        elif self.exit_race_over_button_rect.collidepoint(self.game.scaled_mouse_pos):
            self.race_over_image_right = self.race_over_image_hover_2
            self.race_over_hover_index = 2
        else:
            self.race_over_image_right = self.race_over_default_image_right
            self.race_over_hover_index = 0
        if previous_index != self.race_over_hover_index and self.race_over_hover_index != 0:
            self.game.hover_sound.play()
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

    def _draw_ghost(self):
        """Retrieves the ghost's position at this frame and draws it on the screen, returning False if the ghost has finished the race"""
        try:
            found: bool = False
            with open(self.ghost_filename, newline="") as file:
                reader = csv.reader(file)
                for i, row in enumerate(reader):
                    if i != self.next_ghost_index:
                        continue
                    (
                        self.ghost_car.x,
                        self.ghost_car.y,
                        self.ghost_car.move_angle,
                        self.ghost_car.car_angle,
                    ) = map(float, row)
                    self.ghost_car.draw(self.camera_x, self.camera_y)
                    found = True
                    break
            self.ghost_done = not found
        except (FileNotFoundError, IndexError, ValueError):
            self.ghost_found = False
        except Exception:
            self.ghost_found = False

    def _format_time_simple(self) -> str:
        """Formats time in MM:SS:ms"""
        minutes: int = int(self.elapsed_race_time_s // 60)
        seconds: int = int(self.elapsed_race_time_s % 60)
        milliseconds: int = int((self.elapsed_race_time_ms % 1000) // 10)
        return f"{minutes:02}:{seconds:02}:{milliseconds:02}"

    def _draw_race_over_menu(self) -> None:
        """Draws the race over menu buttons onto the game_surface"""

        # Wait for a second before displaying the screen
        current_time: int = pygame.time.get_ticks()
        time_elapsed: int = current_time - self.race_end_time_ms
        wait_time: int = 1000
        if time_elapsed < wait_time:
            return

        # Control transition
        transition_time_elapsed_ms: int = time_elapsed - wait_time
        transition_duration_ms: int = 250
        percent_progress: float = min(transition_time_elapsed_ms, transition_duration_ms) / transition_duration_ms

        # Adjust and blit the semi-transparent overlay
        dark_overlay_opacity: int = int(percent_progress * constants.PAUSE_OVERLAY_OPACITY)
        dark_overlay_color: tuple[int, int, int, int] = (0, 0, 0, dark_overlay_opacity)
        self.dark_overlay.fill(dark_overlay_color)
        self.game.game_surface.blit(self.dark_overlay, (0, 0))

        # Draw the final time after a small wait time
        show_time_start: int = wait_time + transition_duration_ms + 250
        if time_elapsed > show_time_start:
            self.game.game_surface.blit(self.time_shadow_surface, self.time_shadow_rect)
            self.game.game_surface.blit(self.time_surface, self.time_rect)

        # Calculate the coordinates and blit the images to the game surface
        left_image_x: int = int(percent_progress * constants.WIDTH) - constants.WIDTH
        right_image_x: int = constants.WIDTH - int(percent_progress * constants.WIDTH)
        self.game.game_surface.blit(self.race_over_image_left, (left_image_x, 0))
        self.game.game_surface.blit(self.race_over_image_right, (right_image_x, 0))