from moviepy import VideoFileClip
import pygame

import constants


class TitleScreen:
    """Handles the title screen."""

    def __init__(self, screen, save_manager) -> None:
        self.screen: pygame.Surface = screen
        self.save_manager = save_manager

        # Background image
        self.title_background_image: pygame.Surface = pygame.image.load(
            constants.GENERAL_IMAGE_PATH.format(name="background")).convert()
        self.title_background_image = pygame.transform.scale(self.title_background_image,
                                                             (constants.WIDTH, constants.HEIGHT))

        # Foreground images
        self.title_default_image: pygame.Surface = pygame.image.load(
            constants.TITLE_IMAGE_PATH.format(image_type="default")).convert_alpha()
        self.title_default_image = pygame.transform.scale(self.title_default_image, (constants.WIDTH, constants.HEIGHT))
        self.title_hover_image: pygame.Surface = pygame.image.load(
            constants.TITLE_IMAGE_PATH.format(image_type="hover")).convert_alpha()
        self.title_hover_image = pygame.transform.scale(self.title_hover_image, (constants.WIDTH, constants.HEIGHT))
        self.title_click_image: pygame.Surface = pygame.image.load(
            constants.TITLE_IMAGE_PATH.format(image_type="click")).convert_alpha()
        self.title_click_image = pygame.transform.scale(self.title_click_image, (constants.WIDTH, constants.HEIGHT))
        self.current_image: pygame.Surface = self.title_default_image

        # Start button
        button_width: int = 425
        button_height: int = 200
        button_x: float = (constants.WIDTH - button_width) / 2
        button_y: int = constants.HEIGHT - 405
        self.button_rect: pygame.Rect = pygame.Rect(button_x, button_y, button_width, button_height)

        # --- MODIFIED: Settings Button ---
        try:
            self.settings_icon_default = pygame.image.load(constants.SETTINGS_ICON_PATH).convert_alpha()
            self.settings_icon_default = pygame.transform.scale(self.settings_icon_default, (50, 50))

            # Load the hover icon, but do NOT apply the tint
            self.settings_icon_hover = pygame.image.load(constants.SETTINGS_ICON_PATH).convert_alpha()
            self.settings_icon_hover = pygame.transform.scale(self.settings_icon_hover, (50, 50))

            # REMOVED this line:
            # self.settings_icon_hover.fill((50, 50, 50), special_flags=pygame.BLEND_RGB_ADD)

            # Position at the BOTTOM RIGHT
            self.settings_icon_rect = self.settings_icon_default.get_rect(
                bottomright=(constants.WIDTH - 20, constants.HEIGHT - 20)
            )

        except pygame.error as e:
            print(f"Error loading settings icon: {e}")
            self.settings_icon_default = None
            self.settings_icon_hover = None
            self.settings_icon_rect = pygame.Rect(0, 0, 0, 0)  # dummy rect
        # --- End Modify ---

        # Intro video
        self.intro_clip: VideoFileClip = VideoFileClip(constants.INTRO_VIDEO_PATH)

        # Button hovering
        self.hover_sound: pygame.mixer.Sound = pygame.mixer.Sound(constants.HOVER_SOUND_PATH)
        self.hover_sound.set_volume(self.save_manager.get_volumes()["sfx"])
        self.hover_sound_played: bool = False
        self.last_hovered: int = 0  # 0=None, 1=Start, 2=Settings

        # Transitions
        self.transitioning: bool = False
        self.transitioning_to_next: bool = False
        self.transitioning_from_next: bool = False
        self.transition_start_time_ms: int = 0
        self.transition_next_duration_ms: int = 400
        self.transition_next_pause_time: int = 0

    def play_intro(self, screen: pygame.Surface) -> bool:
        """Plays the intro video before displaying the title screen."""
        intro_sound = pygame.mixer.Sound(constants.INTRO_AUDIO_PATH)
        intro_sound.play()
        clock = pygame.time.Clock()
        try:
            for frame in self.intro_clip.iter_frames(fps=self.intro_clip.fps, dtype="uint8"):
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return False
                    if event.type == pygame.VIDEORESIZE:
                        screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)

                surface = pygame.image.frombuffer(frame.tobytes(), self.intro_clip.size, "RGB")

                # --- Letterbox Logic ---
                window_width, window_height = screen.get_size()
                game_width, game_height = self.intro_clip.size

                if window_width == 0 or window_height == 0:
                    continue  # Skip frame if minimized

                window_aspect = window_width / window_height
                game_aspect = game_width / game_height

                scale_factor: float
                if window_aspect > game_aspect:
                    scale_factor = window_height / game_height
                    new_height = window_height
                    new_width = int(game_width * scale_factor)
                else:
                    scale_factor = window_width / game_width
                    new_width = window_width
                    new_height = int(game_height * scale_factor)

                offset_x = (window_width - new_width) // 2
                offset_y = (window_height - new_height) // 2

                scaled_surface = pygame.transform.scale(surface, (new_width, new_height))
                screen.fill((0, 0, 0))
                screen.blit(scaled_surface, (offset_x, offset_y))
                pygame.display.flip()
                clock.tick(self.intro_clip.fps)
        finally:
            self.intro_clip.close()
        return True

    def handle_events(self, events, mouse_pos: tuple[int, int]) -> str:
        """Handles events like button presses."""
        # Note: mouse_pos is already scaled

        if self.transitioning:
            return ""

        hovered_index: int

        if self.button_rect.collidepoint(mouse_pos):
            hovered_index = 1
        elif self.settings_icon_default and self.settings_icon_rect.collidepoint(mouse_pos):
            hovered_index = 2
        else:
            hovered_index = 0

        if hovered_index != self.last_hovered:
            self.last_hovered = hovered_index

            if hovered_index == 1:
                self.hover_sound.play()
                self.current_image = self.title_hover_image
            elif hovered_index == 2:
                self.hover_sound.play()
                self.current_image = self.title_default_image  # Keep default bg
            else:
                self.current_image = self.title_default_image

        for event in events:
            if event.type == pygame.QUIT:
                return "exit"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if hovered_index == 1:
                    self.current_image = self.title_click_image
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if hovered_index == 1:
                    self.current_image = self.title_default_image
                    return "track_selection"
                elif hovered_index == 2:
                    return "settings"
        return ""

    def handle_transitions(self):
        foreground_image_x: int = 0
        if self.transitioning_to_next:
            current_time: int = pygame.time.get_ticks()
            time_elapsed_ms: int = current_time - self.transition_start_time_ms
            if time_elapsed_ms >= self.transition_next_duration_ms + self.transition_next_pause_time:
                foreground_image_x = -constants.WIDTH
                self.end_transition()
            else:
                transition_time_elapsed_ms: int = min(time_elapsed_ms, self.transition_next_duration_ms)
                percent_progress: float = transition_time_elapsed_ms / self.transition_next_duration_ms
                foreground_image_x = int(-percent_progress * constants.WIDTH)
                self.screen.blit(self.current_image, (foreground_image_x, 0))
        elif self.transitioning_from_next:
            current_time: int = pygame.time.get_ticks()
            time_elapsed_ms: int = current_time - self.transition_start_time_ms
            if time_elapsed_ms >= self.transition_next_duration_ms:
                foreground_image_x = 0
                self.end_transition()
            else:
                transition_time_elapsed_ms: int = min(time_elapsed_ms, self.transition_next_duration_ms)
                percent_progress: float = transition_time_elapsed_ms / self.transition_next_duration_ms
                foreground_image_x = int(percent_progress * constants.WIDTH) - constants.WIDTH
        self.screen.blit(self.current_image, (foreground_image_x, 0))

    def draw(self) -> None:
        """Draws the title screen."""
        self.screen.blit(self.title_background_image, (0, 0))
        self.handle_transitions()

        # --- MODIFIED: Draw Settings Icon ---
        if self.settings_icon_default and not self.transitioning:
            if self.last_hovered == 2:
                # Draw the hover icon (which is now just the plain cog)
                self.screen.blit(self.settings_icon_hover, self.settings_icon_rect)
            else:
                # Draw the default icon
                self.screen.blit(self.settings_icon_default, self.settings_icon_rect)
        # --- End Modify ---

    def initialize_transition(self, start_transition: bool, backwards: bool) -> None:
        """Set flags and store the starting time of the transition"""
        self.transition_start_time_ms: int = pygame.time.get_ticks()
        self.transitioning = True
        self.transitioning_to_next = start_transition and not backwards
        self.transitioning_from_next = not start_transition and backwards

    def end_transition(self) -> None:
        """Reset flags after the transition is complete"""
        self.transitioning = False
        self.transitioning_to_next = False
        self.transitioning_from_next = False