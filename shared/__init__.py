"""
This module initializes the shared package and exports common data structures and enums.
"""
from .where import Where
from .enemy_enum import *
from .direction import Direction
from .state_name import StateName
from .weapon_utils import BasicBulletInfo
from .debug_elements import DebugElements
from .game_state import *

__all__ = [
    "Where",
    "Direction",
    "StateName",
    "EnemyName",
    "EnemyAction",
    "get_enemy_name",
    "BasicBulletInfo",
    "DebugElements",
    "GameState",
    "GameMode",
    "Difficulty",
    "PlayerStats"
]
