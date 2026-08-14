from moviepy import VideoFileClip
import pygame

from ..utilities import constants
from ..utilities import utilities
from ..enums.game_state import GameState
from ..types.menu_results import MenuResults


class TitleScreen:
    """Handles the title screen."""

    SETTINGS_ICON_PATH: str = "assets/images/general/setting_icon.png"
    TITLE_IMAGE_PATH: str = "assets/images/title_screen/{image_type}.png"
    INTRO_VIDEO_PATH: str = "assets/videos/intro.mp4"
    INTRO_AUDIO_PATH: str = "assets/videos/intro.mp3"

    def __init__(self, sound_manager, screen, save_manager) -> None:

        # General
        self.name: str = "title_screen"
        self.sound_manager = sound_manager
        self.screen: pygame.Surface = screen
        self.save_manager = save_manager

        # Background image
        self.title_background_image: pygame.Surface = pygame.image.load(
            constants.GENERAL_IMAGE_PATH.format(name="background")).convert()
        self.title_background_image = pygame.transform.scale(self.title_background_image,
                                                             (constants.WIDTH, constants.HEIGHT))

        # Foreground images
        self.title_default_image: pygame.Surface = pygame.image.load(
            self.TITLE_IMAGE_PATH.format(image_type="default")).convert_alpha()
        self.title_default_image = pygame.transform.scale(self.title_default_image, (constants.WIDTH, constants.HEIGHT))
        self.title_hover_image: pygame.Surface = pygame.image.load(
            self.TITLE_IMAGE_PATH.format(image_type="hover")).convert_alpha()
        self.title_hover_image = pygame.transform.scale(self.title_hover_image, (constants.WIDTH, constants.HEIGHT))
        self.title_click_image: pygame.Surface = pygame.image.load(
            self.TITLE_IMAGE_PATH.format(image_type="click")).convert_alpha()
        self.title_click_image = pygame.transform.scale(self.title_click_image, (constants.WIDTH, constants.HEIGHT))
        self.current_image: pygame.Surface = self.title_default_image

        # Start button
        button_width: int = 425
        button_height: int = 200
        button_x: float = (constants.WIDTH - button_width) / 2
        button_y: int = constants.HEIGHT - 405
        self.button_rect: pygame.Rect = pygame.Rect(button_x, button_y, button_width, button_height)

        # Settings Button
        try:
            self.settings_icon_default = pygame.image.load(self.SETTINGS_ICON_PATH).convert_alpha()
            self.settings_icon_default = pygame.transform.scale(self.settings_icon_default, (50, 50))

            # Load the hover icon, but do NOT apply the tint
            self.settings_icon_hover = pygame.image.load(self.SETTINGS_ICON_PATH).convert_alpha()
            self.settings_icon_hover = pygame.transform.scale(self.settings_icon_hover, (50, 50))

            # Position at the BOTTOM RIGHT
            self.settings_icon_rect = self.settings_icon_default.get_rect(
                bottomright=(constants.WIDTH - 20, constants.HEIGHT - 20)
            )

        except pygame.error as e:
            print(f"Error loading settings icon: {e}")
            self.settings_icon_default = None
            self.settings_icon_hover = None
            self.settings_icon_rect = pygame.Rect(0, 0, 0, 0)  # dummy rect

        # Intro video
        self.intro_clip: VideoFileClip = VideoFileClip(self.INTRO_VIDEO_PATH)

        # Button hovering
        self.hover_sound_played: bool = False
        self.last_hovered: int = 0  # 0=None, 1=Start, 2=Settings

    def play_intro(self, screen: pygame.Surface) -> bool:
        """Plays the intro video before displaying the title screen."""
        intro_sound = pygame.mixer.Sound(self.INTRO_AUDIO_PATH)
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

    def handle_events(self, events, mouse_pos: tuple[int, int]) -> MenuResults | None:
        """Handles events like button presses."""

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
                self.sound_manager.play_hover()
                self.current_image = self.title_hover_image
            elif hovered_index == 2:
                self.sound_manager.play_hover()
                self.current_image = self.title_default_image
            else:
                self.current_image = self.title_default_image

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if hovered_index == 1:
                    self.current_image = self.title_click_image
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if hovered_index == 1:
                    self.current_image = self.title_default_image
                    return MenuResults(next_state=GameState.SAVE_FILE_MENU)
                elif hovered_index == 2:
                    return MenuResults(next_state=GameState.SETTINGS_MENU)
        return None

    def _draw_content(self, x_offset: int = 0):
        """Draws the foreground and settings icon at the given offset."""
        self.screen.blit(self.current_image, (x_offset, 0))

        if self.settings_icon_default:
            icon_to_draw = self.settings_icon_default
            if self.last_hovered == 2:
                icon_to_draw = self.settings_icon_hover

            # Draw icon at its rect position, offset by the transition
            icon_rect = self.settings_icon_rect.move(x_offset, 0)
            self.screen.blit(icon_to_draw, icon_rect)

    def draw(self) -> None:
        """Draws the title screen."""
        self.screen.blit(self.title_background_image, (0, 0))
        self._draw_content(0)
