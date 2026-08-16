
import asyncio

import pygame

from game.game import Game


async def main() -> None:
    pygame.init()
    pygame.font.init()
    pygame.mixer.init()

    game: Game = Game()
    await game.start()


asyncio.run(main())