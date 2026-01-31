from dataclasses import dataclass
import pygame
from pymunk import Vec2d


@dataclass
class Effect:
    pos: Vec2d
    size: float
    opacity: float
    color: tuple[int, int, int] | str
