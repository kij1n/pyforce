"""
This module defines the Where dataclass used for conveying entity state for rendering.
"""
from dataclasses import dataclass
from pygame import Rect


@dataclass
class Where:
    """
    The Where dataclass stores all necessary information to render an entity on the screen.

    Attributes:
        position (tuple[int, int]): The absolute world position of the entity.
        name (str): The name of the entity (e.g., 'player', 'skeleton').
        state (str): The current state/animation of the entity (e.g., 'idle', 'run').
        sprite_index (int): The current frame index of the animation.
        inversion (bool): Whether the sprite should be horizontally flipped.
        arm_deg (int): The rotation angle of the entity's arm, if applicable.
        gun_name (str): The name of the gun the entity is holding, if applicable.
        hitbox (Rect): The pygame Rect representing the entity's physical bounds.
        health_percent (float): The current health of the entity as a percentage (0.0 to 1.0).
        is_dead (bool): Flag indicating if the entity is dead.
    """
    position: tuple[int, int]
    name: str
    state: str
    sprite_index: int
    inversion: bool
    arm_deg: int
    gun_name: str
    hitbox: Rect
    health_percent: float
    is_dead: bool = False  # used for player
