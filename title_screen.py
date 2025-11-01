from moviepy import VideoFileClip
import pygame

import constants


class TitleScreen:
    """Handles the title screen."""

    def __init__(self, screen) -> None:
        self.screen: pygame.Surface = screen
        self.title_default_image: pygame.Surface = pygame.image.load(constants.TITLE_IMAGE_PATH.format(image_type="default")).convert()
        self.title_default_image = pygame.transform.scale(self.title_default_image, (constants.WIDTH, constants.HEIGHT))
        self.title_hover_image: pygame.Surface = pygame.image.load(constants.TITLE_IMAGE_PATH.format(image_type="hover")).convert()
        self.title_hover_image = pygame.transform.scale(self.title_hover_image, (constants.WIDTH, constants.HEIGHT))
        self.title_click_image: pygame.Surface = pygame.image.load(constants.TITLE_IMAGE_PATH.format(image_type="click")).convert()
        self.title_click_image = pygame.transform.scale(self.title_click_image, (constants.WIDTH, constants.HEIGHT))
        self.current_image: pygame.Surface = self.title_default_image
        button_width: int = 425
        button_height: int = 200
        button_x: float = (constants.WIDTH - button_width) / 2
        button_y: int = constants.HEIGHT - 405
        self.button_rect: pygame.Rect = pygame.Rect(button_x, button_y, button_width, button_height)
        self.intro_clip: VideoFileClip = VideoFileClip(constants.INTRO_VIDEO_PATH)

    def play_intro(self) -> bool:
        """Plays the intro video before displaying the title screen."""
        intro_sound = pygame.mixer.Sound(constants.INTRO_AUDIO_PATH)
        intro_sound.play()
        clock = pygame.time.Clock()
        try:
            for frame in self.intro_clip.iter_frames(fps=self.intro_clip.fps, dtype="uint8"):
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return False
                surface = pygame.image.frombuffer(frame.tobytes(), self.intro_clip.size, "RGB")
                scaled_surface = pygame.transform.scale(surface, (constants.WIDTH, constants.HEIGHT))
                self.screen.blit(scaled_surface, (0, 0))
                pygame.display.flip()
                clock.tick(self.intro_clip.fps)
        finally:
            self.intro_clip.close()
        return True

    def handle_events(self, events) -> str:
        """Handles events like button presses."""
        mouse_pos: tuple[int, int] = pygame.mouse.get_pos()
        if self.button_rect.collidepoint(mouse_pos):
            self.current_image = self.title_hover_image
        else:
            self.current_image = self.title_default_image
        for event in events:
            if event.type == pygame.QUIT:
                return "exit"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.button_rect.collidepoint(mouse_pos):
                    self.current_image = self.title_click_image
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if self.button_rect.collidepoint(mouse_pos):
                    self.current_image = self.title_default_image
                    return "track_selection"
        return ""

    def draw(self) -> None:
        """Draws the title screen."""
        self.screen.blit(self.current_image, (0, 0))