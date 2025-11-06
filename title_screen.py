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