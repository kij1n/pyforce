"""
This module defines the GameState enum representing the overall state of the application.
"""
from enum import Enum


class GameState(Enum):
    """
    Enum representing the main states of the game.
    """
    MENU = "menu"
    PAUSE = "pause"
    PLAYING = "playing"
    QUIT = "quit"
