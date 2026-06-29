from dataclasses import dataclass
from pyforce.constants import Difficulty, GameMode


@dataclass
class PlayerStats:
    killed_enemies: int = 0
    time_elapsed: float = 0
    difficulty: Difficulty | None = None
    game_mode: GameMode | None = None
    username: str | None = None
