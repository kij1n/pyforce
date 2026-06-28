from dataclasses import dataclass
from constants import Difficulty, GameMode

@dataclass
class PlayerStats:
    killed_enemies: int = 0
    time_elapsed: float = 0
    difficulty: Difficulty = None
    game_mode: GameMode = None
    username: str = None
