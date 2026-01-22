"""
This module contains utility dataclasses for weaponry and projectiles.
"""
from dataclasses import dataclass
from pymunk import Vec2d


@dataclass
class BasicBulletInfo:
    """
    The BasicBulletInfo dataclass stores properties of a simple bullet.

    Attributes:
        id (int): Unique identifier for the bullet.
        start_pos (Vec2d): The starting position of the bullet in world coordinates.
        reach (float): The maximum distance the bullet can travel.
        damage (int): The amount of damage the bullet deals.
        name (str): The name or type of the bullet.
    """
    id: int
    start_pos: Vec2d
    reach: float
    damage: int
    name: str
