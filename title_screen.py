from moviepy import VideoFileClip
import pygame

import constants


class TitleScreen:
    """Handles the title screen."""

    def __init__(self, screen) -> None:
        self.screen: pygame.Surface = screen

        # Background images
        self.title_default_image: pygame.Surface = pygame.image.load(
            constants.TITLE_IMAGE_PATH.format(image_type="default")).convert()
        self.title_default_image = pygame.transform.scale(self.title_default_image, (constants.WIDTH, constants.HEIGHT))
        self.title_hover_image: pygame.Surface = pygame.image.load(
            constants.TITLE_IMAGE_PATH.format(image_type="hover")).convert()
        self.title_hover_image = pygame.transform.scale(self.title_hover_image, (constants.WIDTH, constants.HEIGHT))
        self.title_click_image: pygame.Surface = pygame.image.load(
            constants.TITLE_IMAGE_PATH.format(image_type="click")).convert()
        self.title_click_image = pygame.transform.scale(self.title_click_image, (constants.WIDTH, constants.HEIGHT))
        self.current_image: pygame.Surface = self.title_default_image

        # Start button
        button_width: int = 425
        button_height: int = 200
        button_x: float = (constants.WIDTH - button_width) / 2
        button_y: int = constants.HEIGHT - 405
        self.button_rect: pygame.Rect = pygame.Rect(button_x, button_y, button_width, button_height)

        # Intro video
        self.intro_clip: VideoFileClip = VideoFileClip(constants.INTRO_VIDEO_PATH)

        # Button hovering
        self.hover_sound: pygame.mixer.Sound = pygame.mixer.Sound(constants.HOVER_SOUND_PATH)
        self.hover_sound.set_volume(0.1)
        self.hover_sound_played: bool = False
        self.last_hovered: int = 0

    def _scale_mouse_pos(self, pos: tuple[int, int], window_size: tuple[int, int]) -> tuple[int, int]:
        """Scales mouse position from window coordinates to game_surface coordinates."""
        game_surface_size = self.screen.get_size()
        if window_size[0] == 0 or window_size[1] == 0:
            return 0, 0
        scale_x = game_surface_size[0] / window_size[0]
        scale_y = game_surface_size[1] / window_size[1]
        return int(pos[0] * scale_x), int(pos[1] * scale_y)

    def play_intro(self, real_screen: pygame.Surface) -> bool:
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
                        real_screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)

                surface = pygame.image.frombuffer(frame.tobytes(), self.intro_clip.size, "RGB")
                scaled_surface = pygame.transform.scale(surface, (constants.WIDTH, constants.HEIGHT))
                self.screen.blit(scaled_surface, (0, 0))  # Blit to game_surface

                scaled_frame_to_window = pygame.transform.scale(self.screen, real_screen.get_size())
                real_screen.blit(scaled_frame_to_window, (0, 0))
                pygame.display.flip()
                clock.tick(self.intro_clip.fps)
        finally:
            self.intro_clip.close()
        return True

    def handle_events(self, events, window_size: tuple[int, int]) -> str:
        """Handles events like button presses."""
        unscaled_mouse_pos: tuple[int, int] = pygame.mouse.get_pos()
        mouse_pos: tuple[int, int] = self._scale_mouse_pos(unscaled_mouse_pos, window_size)
        hovered_index: int

        if self.button_rect.collidepoint(mouse_pos):
            hovered_index = 1
        else:
            hovered_index = 0

        if hovered_index != self.last_hovered:
            self.last_hovered = hovered_index

            if hovered_index == 1:
                self.hover_sound.play()
                self.current_image = self.title_hover_image
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
        return ""

    def draw(self) -> None:
        """Draws the title screen."""
        self.screen.blit(self.current_image, (0, 0))
