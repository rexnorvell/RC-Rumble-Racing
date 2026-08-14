import csv
import json
from pathlib import Path
from typing import Optional

import pygame

from .car import Car
from .cpu_car import CpuCar
from .ghost_car import GhostCar
from ..utilities import constants
from ..utilities.save_manager import SaveManager
from ..utilities.sound_manager import SoundManager
from .track import Track
from ..utilities import utilities
from ..enums.difficulty import Difficulty
from ..enums.track_name import TrackName


class Race:

    NUM_LAPS: dict[str, int] = {
        constants.TRACK_NAMES[0]: 3,
        constants.TRACK_NAMES[1]: 3,
        constants.TRACK_NAMES[2]: 3,
        constants.TRACK_NAMES[3]: 3
    }
    CHECKPOINT_ANGLES: dict[str, int] = {
        constants.TRACK_NAMES[0]: 180, 
        constants.TRACK_NAMES[1]: 90, 
        constants.TRACK_NAMES[2]: 180, 
        constants.TRACK_NAMES[3]: 180
    }

    # Pause Menu
    PAUSE_MENU_IMAGE_PATH: str = "assets/images/pause/{image_name}.png"
    PAUSE_OVERLAY_OPACITY: int = 100
    PAUSE_BUTTON_WIDTH: int = 720
    PAUSE_BUTTON_HEIGHT: int = 85
    PAUSE_RESUME_Y: int = 288
    PAUSE_REPLAY_Y: int = 419
    PAUSE_EXIT_Y: int = 548

    # Race Over Menu
    RACE_OVER_IMAGE_PATH: str = "assets/images/race_over/{image_name}.png"
    RACE_OVER_BUTTON_WIDTH: int = 720
    RACE_OVER_BUTTON_HEIGHT: int = 85
    RACE_OVER_RETRY_Y: int = 419
    RACE_OVER_EXIT_Y: int = 548

    PERSONAL_BEST_FILE_PATH: str = "assets/replays/{track_name}/personal_best.csv"
    PERSONAL_BEST_FILE_NAME: str = "personal_best.csv"

    CPU_GHOST_FILE_PATH: str = "assets/ghosts/{track_name}/track_path.csv"

    ENGINE_IDLE_SOUND_PATH: str = "assets/audio/general/engine_idle.mp3"
    ENGINE_OFF_SOUND_PATH: str = "assets/audio/general/engine_off.mp3"
    ENGINE_REV_SOUND_PATH: str = "assets/audio/general/engine_rev.mp3"

    def __init__(self, game, sound_manager: SoundManager, track_name: TrackName, car_index: int, style_index: int, difficulty: Difficulty,
                 save_manager: SaveManager) -> None:

        # General
        self.game = game
        self.sound_manager = sound_manager
        self.save_manager: SaveManager = save_manager
        self.difficulty: Difficulty = difficulty

        # Get settings
        self.key_bindings = self.save_manager.get_key_bindings()
        self.sfx_volume = self.save_manager.get_volumes()["sfx"]

        # Track
        self.track_name: TrackName = track_name
        self.track: Track = Track(self.track_name)

        # Race Result State
        self.race_result: str | None = None  # "win" or "lose"

        # Pause menu
        self.pause_hover_index: int = 0
        self.is_paused: bool = False
        self.pause_start_time_ms: int = 0
        self.pause_start_time_s: float = 0.0

        self.dark_overlay: pygame.Surface = pygame.Surface((constants.WIDTH, constants.HEIGHT), pygame.SRCALPHA)
        self.dark_overlay.fill((0, 0, 0, self.PAUSE_OVERLAY_OPACITY))
        button_x: float = (constants.WIDTH - self.PAUSE_BUTTON_WIDTH) / 2
        self.resume_button_rect: pygame.Rect = pygame.Rect(button_x, self.PAUSE_RESUME_Y,
                                                           self.PAUSE_BUTTON_WIDTH, self.PAUSE_BUTTON_HEIGHT)
        self.replay_button_rect: pygame.Rect = pygame.Rect(button_x, self.PAUSE_REPLAY_Y,
                                                           self.PAUSE_BUTTON_WIDTH, self.PAUSE_BUTTON_HEIGHT)
        self.exit_button_rect: pygame.Rect = pygame.Rect(button_x, self.PAUSE_EXIT_Y, self.PAUSE_BUTTON_WIDTH,
                                                         self.PAUSE_BUTTON_HEIGHT)

        # Pause Images
        self.pause_image_left: pygame.Surface = pygame.image.load(
            self.PAUSE_MENU_IMAGE_PATH.format(image_name="left")).convert_alpha()
        self.pause_image_left = pygame.transform.scale(self.pause_image_left, (constants.WIDTH, constants.HEIGHT))
        self.pause_default_image_right: pygame.Surface = pygame.image.load(
            self.PAUSE_MENU_IMAGE_PATH.format(image_name="right")).convert_alpha()
        self.pause_default_image_right = pygame.transform.scale(self.pause_default_image_right,
                                                                (constants.WIDTH, constants.HEIGHT))
        self.pause_image_hover_1: pygame.Surface = pygame.image.load(
            self.PAUSE_MENU_IMAGE_PATH.format(image_name="1")).convert_alpha()
        self.pause_image_hover_1 = pygame.transform.scale(self.pause_image_hover_1, (constants.WIDTH, constants.HEIGHT))
        self.pause_image_hover_2: pygame.Surface = pygame.image.load(
            self.PAUSE_MENU_IMAGE_PATH.format(image_name="2")).convert_alpha()
        self.pause_image_hover_2 = pygame.transform.scale(self.pause_image_hover_2, (constants.WIDTH, constants.HEIGHT))
        self.pause_image_hover_3: pygame.Surface = pygame.image.load(
            self.PAUSE_MENU_IMAGE_PATH.format(image_name="3")).convert_alpha()
        self.pause_image_hover_3 = pygame.transform.scale(self.pause_image_hover_3, (constants.WIDTH, constants.HEIGHT))
        self.pause_image_right: pygame.Surface = self.pause_default_image_right

        # Replay
        self.current_race_file: Path = Path(constants.REPLAY_FILE_PATH.format(track_name=self.track.name.value))

        # Race Over Menu Variables
        self.race_over_hover_index: int = 0

        # Calculate SOURCE Rects
        race_over_btn_x = (constants.WIDTH - self.RACE_OVER_BUTTON_WIDTH) // 2
        self.source_retry_rect = pygame.Rect(race_over_btn_x, self.RACE_OVER_RETRY_Y,
                                             self.RACE_OVER_BUTTON_WIDTH, self.RACE_OVER_BUTTON_HEIGHT)
        self.source_exit_rect = pygame.Rect(race_over_btn_x, self.RACE_OVER_EXIT_Y,
                                            self.RACE_OVER_BUTTON_WIDTH, self.RACE_OVER_BUTTON_HEIGHT)

        self.retry_button_rect: pygame.Rect = pygame.Rect(0, 0, 0, 0)
        self.exit_race_over_button_rect: pygame.Rect = pygame.Rect(0, 0, 0, 0)

        # Load Race Over Images
        self.race_over_image_left: pygame.Surface = pygame.image.load(
            self.RACE_OVER_IMAGE_PATH.format(image_name="left")).convert_alpha()
        self.race_over_image_left = pygame.transform.scale(self.race_over_image_left,
                                                           (constants.WIDTH, constants.HEIGHT))

        self.race_over_default: pygame.Surface = pygame.image.load(
            self.RACE_OVER_IMAGE_PATH.format(image_name="right")).convert_alpha()
        self.race_over_default = pygame.transform.scale(self.race_over_default, (constants.WIDTH, constants.HEIGHT))

        self.race_over_hover_1: pygame.Surface = pygame.image.load(
            self.RACE_OVER_IMAGE_PATH.format(image_name="1")).convert_alpha()
        self.race_over_hover_1 = pygame.transform.scale(self.race_over_hover_1, (constants.WIDTH, constants.HEIGHT))

        self.race_over_hover_2: pygame.Surface = pygame.image.load(
            self.RACE_OVER_IMAGE_PATH.format(image_name="2")).convert_alpha()
        self.race_over_hover_2 = pygame.transform.scale(self.race_over_hover_2, (constants.WIDTH, constants.HEIGHT))

        # --- CROP BUTTONS ---
        self.btn_retry_default = self.race_over_default.subsurface(self.source_retry_rect).copy()
        self.btn_retry_hover = self.race_over_hover_1.subsurface(self.source_retry_rect).copy()

        self.btn_exit_default = self.race_over_default.subsurface(self.source_exit_rect).copy()
        self.btn_exit_hover = self.race_over_hover_2.subsurface(self.source_exit_rect).copy()

        # Fonts
        self.result_font = pygame.font.Font(constants.TEXT_FONT_PATH, 100)
        self.button_font = pygame.font.Font(constants.TEXT_FONT_PATH, 50)
        self.timer_font: pygame.font.Font = pygame.font.Font(constants.FALLBACK_FONT_PATH, 30)
        self.timer_font.set_bold(True)
        self.time_font: pygame.font.Font = pygame.font.Font(constants.TEXT_FONT_PATH, 60)

        # Sound
        self.next_lap_sound: pygame.mixer.Sound = pygame.mixer.Sound(
            constants.TRACK_AUDIO_PATH.format(track_name="general", song_type="next_lap"))
        self.next_lap_sound.set_volume(self.sfx_volume)
        self.respawn_sound: pygame.mixer.Sound = pygame.mixer.Sound(
            constants.TRACK_AUDIO_PATH.format(track_name="general", song_type="respawn"))
        self.respawn_sound.set_volume(self.sfx_volume)
        self.engine_idle_sound: pygame.mixer.Sound = pygame.mixer.Sound(self.ENGINE_IDLE_SOUND_PATH)
        self.engine_idle_sound.set_volume(self.sfx_volume)
        self.engine_off_sound: pygame.mixer.Sound = pygame.mixer.Sound(self.ENGINE_OFF_SOUND_PATH)
        self.engine_off_sound.set_volume(self.sfx_volume)
        self.engine_rev_sound: pygame.mixer.Sound = pygame.mixer.Sound(self.ENGINE_REV_SOUND_PATH)
        self.engine_rev_sound.set_volume(self.sfx_volume)

        # User Car
        self.user_car_index = car_index
        self.user_style_index = style_index
        self.user_car_config = constants.CAR_DEFINITIONS[self.user_car_index]
        self.user_car: Car = Car(self.game.game_surface, self.track.name, False, self.user_car_config,
                                 self.user_style_index, self.key_bindings)

        # User Data
        self.personal_best_time: float = float("inf")

        # Opponent setup
        self.opponent: Car = None
        self.ghost_found: bool = False
        self.show_ghost: bool = True

        if self.difficulty == Difficulty.PB:
            meta_path = Path(constants.PERSONAL_BEST_METADATA_FILE_PATH.format(track_name=self.track.name.value))
            pb_car_idx = 0
            pb_style_idx = 0
            if meta_path.exists():
                try:
                    with open(meta_path, "r") as f:
                        meta_data = json.load(f)
                        pb_car_idx = meta_data.get("car_type_index", 0)
                        pb_style_idx = meta_data.get("style_index", 0)
                except:
                    pass

            pb_config = constants.CAR_DEFINITIONS[pb_car_idx]
            pb_path = Path(self.PERSONAL_BEST_FILE_PATH.format(track_name=self.track.name.value))

            self.opponent = GhostCar(self.game.game_surface, self.track.name, pb_path, pb_config, pb_style_idx)
            self.ghost_found = pb_path.exists()

        else:
            cpu_path = Path(self.CPU_GHOST_FILE_PATH.format(track_name=self.track.name.value))
            self.opponent = CpuCar(self.game.game_surface, self.track.name, self.difficulty, cpu_path)
            self.ghost_found = cpu_path.exists()

        # Opponent Race State
        self.cpu_current_lap: int = 1
        self.cpu_has_checkpoint: bool = False

        # Time
        self.elapsed_race_time_ms: int = 0
        self.elapsed_race_time_s: float = 0.0
        self.current_time: int = 0

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
        self.wait_time_before_countdown_ms: int = 5000

        # UI Elements
        self.lap_str: str = ""
        self.lap_surf: pygame.Surface = None
        self.lap_shadow: pygame.Surface = None
        self.countdown_font: pygame.font.Font = pygame.font.Font(constants.TEXT_FONT_PATH, 120)

    def _get_current_time(self):
        self.current_time = pygame.time.get_ticks()

    def _next_frame(self):
        self.clock.tick(60)

    def _set_max_speed(self):
        self.user_car.is_off_road = True if self.track.is_off_road(self.user_car.x, self.user_car.y) else False
        self.user_car.set_max_speed()
        # For CPU/Ghost, they handle their own logic/updates, but we set physics flags if needed
        # (Though GhostCar ignores them)
        if isinstance(self.opponent, CpuCar):
            self.opponent.is_off_road = True if self.track.is_off_road(self.opponent.x, self.opponent.y) else False

    def start(self) -> bool:
        """The main game loop when the user is racing on a track"""

        self._initialize_race()
        self.countdown_start_time = pygame.time.get_ticks()

        while self.running:
            self._next_frame()
            self._get_current_time()
            self._get_elapsed_race_time()
            self.game.set_scaled_mouse_pos()
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

                # UPDATE OPPONENT (CPU or GHOST)
                if self.ghost_found and self.show_ghost:
                    self.opponent.update()

                self._check_out_of_bounds()
                self._check_user_lap_completion()
                self._check_cpu_progress()

                if self.elapsed_race_time_s < (self.personal_best_time + 1):
                    self.user_car.log_properties(self.track_name)

            elif self.race_over:
                # --- COASTING LOGIC ---
                self._set_max_speed()

                self.user_car.handle_input({}, False)
                self.user_car.update_position()

                # Coast Opponent (Only if it's CPU, Ghost just stops or finishes replay)
                if self.ghost_found and self.show_ghost and isinstance(self.opponent, CpuCar):
                    if self.opponent.speed > 0:
                        self.opponent.speed -= constants.FRICTION * 1.5
                        if self.opponent.speed < 0: self.opponent.speed = 0
                    elif self.opponent.speed < 0:
                        self.opponent.speed += constants.FRICTION * 1.5
                        if self.opponent.speed > 0: self.opponent.speed = 0
                    self.opponent.move_angle = self.opponent.car_angle
                    self.opponent.update_position()

                if not self.compared_to_best and self.race_result == "win":
                    self._compare_to_best()
                    self._check_unlocks()
                if not self.applause_played:
                    self.applause_played = True
                    self._play_next_track()

                # Handle Menu Inputs
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
        if self.current_race_file.exists():
            self.current_race_file.unlink()
        pygame.mixer.music.stop()
        self.engine_idle_sound.stop()

    def _get_elapsed_race_time(self):
        if self.during_race and not self.is_paused:
            self.elapsed_race_time_ms = self.current_time - self.race_start_time_ms
        elif self.during_race and self.is_paused:
            self.elapsed_race_time_ms = self.pause_start_time_ms - self.race_start_time_ms
        self.elapsed_race_time_s = self.elapsed_race_time_ms / 1000.0

    def _draw_race(self) -> None:
        self.camera_x = self.user_car.x - (constants.WIDTH / 2)
        self.camera_y = self.user_car.y - (constants.HEIGHT / 2)
        self.track.draw(self.game.game_surface, self.camera_x, self.camera_y)

        if self.ghost_found and self.show_ghost:
            self.opponent.draw(self.camera_x, self.camera_y)

        self.user_car.draw(self.camera_x, self.camera_y)

        if not self.race_over:
            self._draw_race_ui()
        if self.is_paused:
            self._draw_pause_menu()
        else:
            if not self.countdown_done:
                self._draw_countdown()

        if self.race_over and not self.is_paused:
            self._draw_race_over_menu()

        if self.is_paused or self.race_over:
            self.game.draw_cursor()

        self.game.draw_letterboxed_surface()
        pygame.display.flip()

    def _draw_pause_menu(self) -> None:
        current_time: int = pygame.time.get_ticks()
        time_elapsed_ms: int = current_time - self.pause_start_time_ms
        transition_duration_ms: int = 250
        percent_progress: float = min(time_elapsed_ms, transition_duration_ms) / transition_duration_ms

        dark_overlay_opacity: int = int(percent_progress * self.PAUSE_OVERLAY_OPACITY)
        dark_overlay_color: tuple[int, int, int, int] = (0, 0, 0, dark_overlay_opacity)
        self.dark_overlay.fill(dark_overlay_color)

        left_image_x: int = int(percent_progress * constants.WIDTH) - constants.WIDTH
        right_image_x: int = constants.WIDTH - int(percent_progress * constants.WIDTH)

        self.game.game_surface.blit(self.dark_overlay, (0, 0))
        self.game.game_surface.blit(self.pause_image_left, (left_image_x, 0))
        self.game.game_surface.blit(self.pause_image_right, (right_image_x, 0))

    def _draw_race_ui(self) -> None:
        total_time_str: str = self._format_time_simple()
        total_time_surf: pygame.Surface = self.timer_font.render(total_time_str, True, constants.TEXT_COLOR)
        total_time_shadow: pygame.Surface = self.timer_font.render(total_time_str, True, constants.TEXT_SHADOW_COLOR)

        self.game.game_surface.blit(self.lap_shadow, (22, 12))
        self.game.game_surface.blit(self.lap_surf, (20, 10))
        self.game.game_surface.blit(total_time_shadow, (22, 52))
        self.game.game_surface.blit(total_time_surf, (20, 50))

    def _initialize_pause(self) -> None:
        pygame.mixer.music.pause()
        self.sound_manager.play_click()
        self.engine_idle_sound.play(-1)
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
        self.events = pygame.event.get()
        for event in self.events:
            if event.type == pygame.QUIT:
                self._clean_up()
                utilities.quit_game()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if not self.race_over:
                        self.is_paused = not self.is_paused
                        if self.is_paused:
                            self._initialize_pause()
                        else:
                            self.engine_idle_sound.fadeout(1000)
                            self._unpause()
                if event.key == self.key_bindings[constants.KEY_ACTION_TOGGLE_GHOST]:
                    self.show_ghost = not self.show_ghost
            if event.type == pygame.VIDEORESIZE:
                self.game.screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)

    def _initialize_race(self) -> None:
        self._get_personal_best_time()
        self._create_replay_file()
        self.ghost_found = (self.opponent and (getattr(self.opponent, 'path_points', False) or getattr(self.opponent, 'recording_data', False)))
        self._render_lap_text()
        self.user_car.set_respawn_point(self.user_car.start_x, self.user_car.start_y, self.user_car.start_angle)
        self._play_next_track()

    def _get_personal_best_time(self) -> None:
        personal_best_metadata_path: Path = Path(constants.PERSONAL_BEST_METADATA_FILE_PATH.format(track_name=self.track.name.value))
        self.personal_best_time = float("inf")
        if personal_best_metadata_path.exists():
            try:
                with open(personal_best_metadata_path, "r") as file:
                    personal_best_data = json.load(file)
                self.personal_best_time = personal_best_data.get("time", float("inf"))
            except (json.JSONDecodeError, IOError):
                print("Error loading personal best metadata")

    def _create_replay_file(self) -> None:
        replay_path = Path(constants.REPLAY_FILE_PATH.format(track_name=self.track.name.value))
        replay_path.parent.mkdir(parents=True, exist_ok=True)
        with replay_path.open("w", newline=""):
            pass

    def _check_unlocks(self):
        """Unlocks difficulties and tracks based on race result"""
        if self.race_result == "win":

            if self.difficulty == Difficulty.EASY:
                self.save_manager.unlock_difficulty(self.track_name, Difficulty.MEDIUM)

            elif self.difficulty == Difficulty.MEDIUM:
                self.save_manager.unlock_difficulty(self.track_name, Difficulty.HARD)

                # ...AND unlocks the Next Track
                next_track = self.save_manager.get_next_track_name(self.track_name)
                if next_track:
                    self.save_manager.unlock_track(next_track)

            #elif self.difficulty == Difficulty.HARD:
                # Winning Hard marks the track as fully COMPLETE
                #self.save_manager.unlock_difficulty(self.track_name, "complete")

    def _play_next_track(self) -> None:
        if self.current_track_index < len(self.track.playlist):
            track_path, loops = self.track.playlist[self.current_track_index]
            pygame.mixer.music.load(track_path)
            pygame.mixer.music.play(loops)
            self.current_track_index += 1

    def _pause(self) -> str:
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
            self.sound_manager.play_hover()
        for event in self.events:
            if event.type == pygame.QUIT:
                self.game.quit()

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if self.pause_hover_index == 1:
                    self.sound_manager.play_click()
                    self.is_paused = False
                    self.engine_idle_sound.fadeout(1000)
                    return "resume"
                elif self.pause_hover_index == 2:
                    self.sound_manager.play_click()
                    self.engine_idle_sound.stop()
                    self.engine_rev_sound.play()
                    pygame.time.wait(int(self.engine_rev_sound.get_length() * 1000))
                    return "replay"
                elif self.pause_hover_index == 3:
                    self.sound_manager.play_click()
                    self.engine_idle_sound.stop()
                    self.engine_off_sound.play()
                    pygame.time.wait(int(self.engine_off_sound.get_length() * 1000))
                    return "exit_to_menu"
        return ""

    def _check_out_of_bounds(self) -> None:
        if self.track.is_out_of_bounds(self.user_car.x, self.user_car.y):
            self.respawn_sound.play()
            self.user_car.respawn()

    def _check_cpu_progress(self) -> None:
        if not self.ghost_found: return

        # Check opponent position (x, y) - works for both CpuCar and GhostCar
        if self.track.check_checkpoint(self.opponent.x, self.opponent.y):
            self.cpu_has_checkpoint = True

        if self.cpu_has_checkpoint and self.track.check_finish_line(self.opponent.x, self.opponent.y):
            self.cpu_has_checkpoint = False
            self.cpu_current_lap += 1
            if self.cpu_current_lap > self.NUM_LAPS[self.track.name]:
                self.race_result = "lose"
                self.during_race = False
                self.race_over = True
                self.race_end_time_ms = pygame.time.get_ticks()

    def _check_user_lap_completion(self) -> None:
        if self.track.check_checkpoint(self.user_car.x, self.user_car.y):
            if not self.has_checkpoint:
                self.has_checkpoint = True
                cp_x = self.track.checkpoint_1.centerx
                cp_y = self.track.checkpoint_1.centery
                cp_angle = self.CHECKPOINT_ANGLES[self.track.name]
                self.user_car.set_respawn_point(cp_x, cp_y, cp_angle)

        if self.has_checkpoint and self.track.check_finish_line(self.user_car.x, self.user_car.y):
            self.has_checkpoint = False
            self.current_lap += 1
            self._render_lap_text()
            start_x = self.user_car.start_x
            start_y = self.user_car.start_y
            start_angle = self.user_car.start_angle
            self.user_car.set_respawn_point(start_x, start_y, start_angle)

            if self.current_lap > self.NUM_LAPS[self.track.name]:
                self.race_result = "win"
                self.during_race = False
                self.race_over = True
                self.race_end_time_ms = pygame.time.get_ticks()
            else:
                if self.current_lap == self.NUM_LAPS[self.track.name]:
                    self._play_next_track()
                else:
                    self.next_lap_sound.play()

    def _draw_countdown(self) -> None:
        elapsed: int = self.current_time - self.countdown_start_time - self.wait_time_before_countdown_ms
        countdown_text: Optional[str] = None
        if 0 < elapsed < 1000:
            countdown_text = "3"
        elif 0 < elapsed < 2000:
            countdown_text = "2"
        elif 0 < elapsed < 3000:
            countdown_text = "1"
        elif 0 < elapsed < 4000:
            if not self.during_race:
                self.during_race = True
                self.race_start_time_ms = pygame.time.get_ticks()
            countdown_text = "Go!"
        elif elapsed >= 4000:
            self.countdown_done = True
        if countdown_text:
            countdown_surface: pygame.Surface = self.countdown_font.render(countdown_text, True, constants.TEXT_COLOR)
            countdown_rect: pygame.Rect = countdown_surface.get_rect(center=(constants.WIDTH / 2, constants.HEIGHT / 2))
            self.game.game_surface.blit(countdown_surface, countdown_rect)

    def _render_lap_text(self):
        self.lap_str: str = f"Lap {self.current_lap}/{self.NUM_LAPS[self.track.name]}"
        self.lap_surf: pygame.Surface = self.timer_font.render(self.lap_str, True, constants.TEXT_COLOR)
        self.lap_shadow: pygame.Surface = self.timer_font.render(self.lap_str, True, constants.TEXT_SHADOW_COLOR)

    def _compare_to_best(self) -> None:
        self.compared_to_best = True
        if self.elapsed_race_time_s < self.personal_best_time:
            personal_best_metadata_path: Path = Path(
                constants.PERSONAL_BEST_METADATA_FILE_PATH.format(track_name=self.track.name.value))
            metadata = {
                "time": self.elapsed_race_time_s,
                "car_type_index": self.user_car_index,
                "style_index": self.user_style_index
            }
            with open(personal_best_metadata_path, "w") as file:
                json.dump(metadata, file)
            if self.current_race_file.exists():
                new_personal_best: Path = self.current_race_file.with_name(self.PERSONAL_BEST_FILE_NAME)
                self.current_race_file.replace(new_personal_best)
            self.personal_best_time = self.elapsed_race_time_s
        if self.current_race_file.exists():
            self.current_race_file.unlink()

    def _handle_race_over_menu(self) -> str:
        current_time = pygame.time.get_ticks()
        if current_time - self.race_end_time_ms < 2500:
            return ""

        previous_index: int = self.race_over_hover_index
        if self.retry_button_rect.collidepoint(self.game.scaled_mouse_pos):
            self.race_over_hover_index = 1
        elif self.exit_race_over_button_rect.collidepoint(self.game.scaled_mouse_pos):
            self.race_over_hover_index = 2
        else:
            self.race_over_hover_index = 0

        if previous_index != self.race_over_hover_index and self.race_over_hover_index != 0:
            self.sound_manager.play_hover()

        for event in self.events:
            if event.type == pygame.QUIT:
                self.game.quit()
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if self.race_over_hover_index == 1:
                    self.sound_manager.play_click()
                    return "replay"
                elif self.race_over_hover_index == 2:
                    self.sound_manager.play_click()
                    return "exit_to_menu"
        return ""

    def _format_time_simple(self) -> str:
        minutes: int = int(self.elapsed_race_time_s // 60)
        seconds: int = int(self.elapsed_race_time_s % 60)
        milliseconds: int = int((self.elapsed_race_time_ms % 1000) // 10)
        return f"{minutes:02}:{seconds:02}:{milliseconds:02}"

    def _draw_race_over_menu(self) -> None:
        """
        Animates the Race Over Screen with Dynamic Elements.
        Phase 1: Win/Lose Box Pops In
        Phase 2: Box Moves Up
        Phase 3: Buttons Drop Down + Time Appfrs in Middle
        """
        current_time = pygame.time.get_ticks()
        time_elapsed = current_time - self.race_end_time_ms

        # 1. Dark Overlay Fade-in
        overlay_progress = min(time_elapsed / 1000.0, 1.0)
        dark_overlay_opacity = int(overlay_progress * self.PAUSE_OVERLAY_OPACITY)
        self.dark_overlay.fill((0, 0, 0, dark_overlay_opacity))
        self.game.game_surface.blit(self.dark_overlay, (0, 0))

        # 2. Animation Variables
        start_center_y = constants.HEIGHT / 2
        end_center_y = 150  # Top of screen

        move_start_time = 1500
        move_duration = 500

        # Calculate Box Position
        if time_elapsed < move_start_time:
            current_center_y = start_center_y
            current_scale = 1.0
        elif time_elapsed < move_start_time + move_duration:
            move_progress = (time_elapsed - move_start_time) / move_duration
            move_progress = 1 - pow(1 - move_progress, 3)  # Ease Out
            current_center_y = start_center_y + (end_center_y - start_center_y) * move_progress
            current_scale = 1.0 - (0.4 * move_progress)  # Scale down to 0.6
        else:
            current_center_y = end_center_y
            current_scale = 0.6

        # 3. Draw Win/Lose Box
        box_width = 600 * current_scale
        box_height = 300 * current_scale
        box_rect = pygame.Rect(0, 0, box_width, box_height)
        box_rect.center = (constants.WIDTH // 2, int(current_center_y))

        # Determine Colors (Green for Win, Red for Lose)
        is_win = self.race_result == "win"
        box_color = (0, 100, 0) if is_win else (100, 0, 0)
        border_color = (0, 255, 0) if is_win else (255, 0, 0)

        # Draw Box Background
        box_surf = pygame.Surface((int(box_width), int(box_height)), pygame.SRCALPHA)
        box_surf.fill((*box_color, 200))
        pygame.draw.rect(box_surf, border_color, box_surf.get_rect(), 5)
        self.game.game_surface.blit(box_surf, box_rect)

        # Draw Win/Lose Text
        result_text = "YOU WIN!" if is_win else "YOU LOSE"
        scaled_font_size = int(100 * current_scale)
        scaled_font = pygame.font.Font(constants.TEXT_FONT_PATH, scaled_font_size)
        text_surf = scaled_font.render(result_text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=box_rect.center)
        self.game.game_surface.blit(text_surf, text_rect)

        # 4. Buttons & Time (Drop Down)
        buttons_start_time = 2000
        buttons_duration = 500

        if time_elapsed > buttons_start_time:
            btn_progress = min((time_elapsed - buttons_start_time) / buttons_duration, 1.0)

            # Animation positions
            start_y = -300
            end_base_y = constants.HEIGHT / 2 + 50

            current_base_y = start_y + (end_base_y - start_y) * btn_progress

            # Button offsets
            retry_y = int(current_base_y)
            exit_y = int(current_base_y) + 110  # Gap between buttons

            # Update Button Rects for Clicking
            center_x = (constants.WIDTH - self.PAUSE_BUTTON_WIDTH) // 2
            self.retry_button_rect = pygame.Rect(center_x, retry_y, self.PAUSE_BUTTON_WIDTH,
                                                 self.PAUSE_BUTTON_HEIGHT)
            self.exit_race_over_button_rect = pygame.Rect(center_x, exit_y, self.PAUSE_BUTTON_WIDTH,
                                                          self.PAUSE_BUTTON_HEIGHT)

            # Draw TIME (Centered in the gap between Box and Buttons)
            time_str = f"{self.elapsed_race_time_s:.2f} s"
            time_surf = self.time_font.render(time_str, True, constants.TEXT_COLOR)
            time_surf.set_alpha(int(255 * btn_progress))
            time_rect = time_surf.get_rect(center=(constants.WIDTH // 2, 340))
            self.game.game_surface.blit(time_surf, time_rect)

            # Draw Buttons (Using Sliced Images)
            # Replay Button
            if self.race_over_hover_index == 1:
                self.game.game_surface.blit(self.btn_retry_hover, self.retry_button_rect)
            else:
                self.game.game_surface.blit(self.btn_retry_default, self.retry_button_rect)

            # Exit Button
            if self.race_over_hover_index == 2:
                self.game.game_surface.blit(self.btn_exit_hover, self.exit_race_over_button_rect)
            else:
                self.game.game_surface.blit(self.btn_exit_default, self.exit_race_over_button_rect)