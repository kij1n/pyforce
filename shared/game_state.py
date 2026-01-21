from enum import Enum


class GameState(Enum):
    MENU = "menu"
    PAUSE = "pause"
    PLAYING = "playing"
    QUIT = "quit"
