from __future__ import annotations

import pygame


class SoundManager:
    HOVER_SOUND_PATH: str = "assets/audio/general/hover.ogg"
    CLICK_SOUND_PATH: str = "assets/audio/general/click.ogg"

    hover_sound: pygame.mixer.Sound
    click_sound: pygame.mixer.Sound

    def __init__(self) -> None:
        self.hover_sound = pygame.mixer.Sound(self.HOVER_SOUND_PATH)
        self.click_sound = pygame.mixer.Sound(self.CLICK_SOUND_PATH)

    def play_hover(self) -> None:
        self.hover_sound.play()

    def play_click(self) -> None:
        self.click_sound.play()