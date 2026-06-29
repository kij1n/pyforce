from __future__ import annotations
from typing import TYPE_CHECKING
from dataclasses import dataclass
from pyforce.structures import Where, DebugElements, Effect, PlayerStats
from pyforce.constants import GameState

if TYPE_CHECKING:
    from pyforce.model.weaponry import Bullet
    from pyforce.model.pickups import Pickup
    from pymunk import Vec2d, Shape


@dataclass
class RenderInfo:
    player_pos: Vec2d
    where_array: list[Where]
    bullets_dict: dict[Bullet, Shape]
    debug_elements: DebugElements
    effects: list[Effect]
    pickups: list[Pickup]
    game_state: GameState | None = None
    player_stats: PlayerStats | None = None
