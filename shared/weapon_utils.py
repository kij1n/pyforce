from dataclasses import dataclass
from pymunk import Vec2d


@dataclass
class BasicBulletInfo:
    id: int
    start_pos: Vec2d
    reach: float
    damage: int
    name: str
