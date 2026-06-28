from dataclasses import dataclass
from pymunk import Vec2d


@dataclass
class Effect:
    pos: Vec2d
    size: float
    opacity: float
    color: tuple[int, int, int] | str
