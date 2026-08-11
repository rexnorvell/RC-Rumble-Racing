from .game.game import Game


def main() -> None:
    game: Game = Game()
    game.start()


if __name__ == "__main__":
    main()