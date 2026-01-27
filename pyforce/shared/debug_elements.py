"""
This module defines the DebugElements dataclass for storing debug-related information.
"""
from __future__ import annotations
from dataclasses import dataclass
import pygame
import pymunk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game_data.entities.patrol_path import PatrolPath


@dataclass
class DebugElements:
    """
    The DebugElements dataclass holds information used for rendering debug visualizations.

    Attributes:
        sim (pymunk.Space): The physics simulation space.
        patrol_paths (list[PatrolPath]): A list of patrol paths to be drawn.
        bbs (list[pygame.Rect]): A list of bounding boxes to be drawn.
    """
    sim: pymunk.Space
    patrol_paths: list[PatrolPath]
    bbs: list[pygame.Rect]
