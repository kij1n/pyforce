"""
This module defines the GameState enum representing the overall state of the application.
"""

from dataclasses import dataclass
from enum import Enum


class GameState(Enum):
    """
    Enum representing the main states of the game.
    """

    MENU = "menu"
    PAUSE = "pause"
    PLAYING = "playing"
    QUIT = "quit"


class GameMode(Enum):
    """
    Enum representing the game modes.
    """

    INFINITE = "infinite"
    SPEEDRUN = "speedrun"


class Difficulty(Enum):
    """
    Enum representing the difficulty levels.
    """

    EASY = "easy"
    NORMAL = "normal"
    HARD = "hard"


@dataclass
class PlayerStats:
    killed_enemies: int = 0
    time_elapsed: float = 0
    difficulty: Difficulty = None
    game_mode: GameMode = None
    username: str = None
