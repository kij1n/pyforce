from __future__ import annotations
from typing import TYPE_CHECKING
from dataclasses import dataclass
from structures import Where, DebugElements, Effect, PlayerStats
from constants import GameState

if TYPE_CHECKING:
    from model.weaponry import Bullet
    from model.pickups import Pickup
    from pymunk import Vec2d, Shape


@dataclass
class RenderInfo:
    player_pos: Vec2d
    where_array: list[Where]
    bullets_dict: dict[Bullet, Shape]
    debug_elements: DebugElements
    effects: list[Effect]
    pickups: list[Pickup]
    game_state: GameState = None
    player_stats: PlayerStats = None
