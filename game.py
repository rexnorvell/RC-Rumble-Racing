import sys
from typing import Optional

import pygame

import constants
from car import Car
from track import Track
from title_screen import TitleScreen


class Game:
    """Manages the overall game state, main loop, and coordination between Car and Track."""

    def __init__(self, track_name: str) -> None:
        pygame.init()
        pygame.font.init()
        pygame.mixer.init()
        self.screen: pygame.Surface = pygame.display.set_mode((constants.WIDTH, constants.HEIGHT))
        self.clock: pygame.time.Clock = pygame.time.Clock()
        pygame.display.set_caption(constants.GAME_TITLE)

        self.track: Track = Track(track_name)
        self.car: Car = Car(self.screen, self.track.name)

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
        self.countdown_start_time: int = pygame.time.get_ticks()

        # Fonts
        self.lap_count_font: pygame.font.Font = pygame.font.Font(constants.TEXT_FONT_PATH, 45)
        self.countdown_font: pygame.font.Font = pygame.font.Font(constants.TEXT_FONT_PATH, 120)

        # Text surfaces
        self.lap_count_text: pygame.Surface
        self.lap_count_text_rect: pygame.Rect
        self._update_lap_text()

    def _play_next_track(self) -> None:
        """Loads and plays the next audio track in the playlist."""
        if self.current_track_index < len(self.track.playlist):
            track_path, loops = self.track.playlist[self.current_track_index]
            pygame.mixer.music.load(track_path)
            pygame.mixer.music.play(loops)
            self.current_track_index += 1

    def _update_lap_text(self, is_finished: bool = False) -> None:
        """Generates the lap counter text surface."""
        text: str
        if is_finished:
            text = "Finish!"
        else:
            text = f"Lap {self.current_lap} of {constants.NUM_LAPS[self.track.name]}"

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
            countdown_text = "Go!"
        else:
            self.before_race = False

        if countdown_text:
            countdown_surface: pygame.Surface = self.countdown_font.render(countdown_text, True, constants.TEXT_COLOR)
            countdown_rect: pygame.Rect = countdown_surface.get_rect(center=(constants.WIDTH / 2, constants.HEIGHT / 2))
            self.screen.blit(countdown_surface, countdown_rect)

    def _display_race_time(self) -> None:
        """Draws the final race time after the race is over."""
        if self.race_start_time is None or self.race_end_time is None:
            return  # Should not happen if race_over is True, but good for type safety

        total_time_ms: int = self.race_end_time - self.race_start_time
        total_seconds: float = total_time_ms / 1000
        formatted_time: str = f"{total_seconds:.2f} s"

        time_font: pygame.font.Font = pygame.font.Font(constants.TEXT_FONT_PATH, 60)
        time_surface: pygame.Surface = time_font.render(formatted_time, True, constants.TEXT_COLOR)
        time_rect: pygame.Rect = time_surface.get_rect(center=(constants.WIDTH / 2, constants.HEIGHT / 2))
        self.screen.blit(time_surface, time_rect)

    def _check_lap_completion(self) -> None:
        """Checks for checkpoint and finish line crosses and updates lap count."""
        if self.track.check_checkpoint(self.car.x, self.car.y):
            self.has_checkpoint = True

        if self.has_checkpoint and self.track.check_finish_line(self.car.x, self.car.y):
            self.has_checkpoint = False
            self.current_lap += 1

            if self.current_lap > constants.NUM_LAPS[self.track.name]:
                self.during_race = False
                self.race_over = True
                self.race_end_time = pygame.time.get_ticks()
                self._update_lap_text(is_finished=True)
            else:
                if self.current_lap == constants.NUM_LAPS[self.track.name]:
                    self._play_next_track()
                self._update_lap_text()

    def welcome(self):
        """Displays the title screen and starts the game when the button is clicked."""
        title_screen: TitleScreen = TitleScreen(self.screen)
        title_clock: pygame.time.Clock = pygame.time.Clock()
        running = True
        while running:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    running = False

            next_action = title_screen.handle_events(events)
            if next_action == "start_game":
                print("Time to start!")
                self.run()

            title_screen.draw()
            title_clock.tick(60)

    def run(self) -> None:
        """The main game loop."""
        self._play_next_track()
        self.countdown_start_time = pygame.time.get_ticks()
        running: bool = True
        while running:
            self.clock.tick(60)
            current_time: int = pygame.time.get_ticks()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            if not pygame.mixer.music.get_busy() and not self.race_over:
                self._play_next_track()

            keys: pygame.key.ScancodeWrapper = pygame.key.get_pressed()
            self.car.handle_input(keys, self.during_race)

            max_speed: float = constants.MAX_SPEED
            if self.track.is_off_road(self.car.x, self.car.y):
                max_speed *= 0.5

            self.car.update_position(max_speed)

            self.track.draw(self.screen)
            self.screen.blit(self.lap_count_text, self.lap_count_text_rect)
            self.car.draw(car_design_id=1)

            if self.before_race:
                self._draw_countdown(current_time)
            elif self.during_race:
                self._check_lap_completion()
            elif self.race_over:
                self._display_race_time()
                if not self.applause_played:
                    self.applause_played = True
                    self._play_next_track()

            pygame.display.flip()

        pygame.quit()
        sys.exit()

