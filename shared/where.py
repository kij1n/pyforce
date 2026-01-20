from dataclasses import dataclass
from pygame import Rect


@dataclass
class Where:
    position: tuple[int, int]
    name: str
    state: str
    sprite_index: int
    inversion: bool
    arm_deg: int
    gun_name: str
    hitbox: Rect
    is_dead: bool = False  # used for player