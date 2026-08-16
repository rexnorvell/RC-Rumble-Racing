from dataclasses import dataclass

from enums.game_state import GameState
from enums.track_name import TrackName
from enums.difficulty import Difficulty


@dataclass
class MenuResults:
    next_state: GameState | None = None
    track_name: TrackName | None = None
    difficulty: Difficulty | None = None
    car_index: int | None = None
    style_index: int | None = None