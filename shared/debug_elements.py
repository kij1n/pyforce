from __future__ import annotations
from dataclasses import dataclass
import pygame
import pymunk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game_data.entities.patrol_path import PatrolPath


@dataclass
class DebugElements:
    sim: pymunk.Space
    patrol_paths: list[PatrolPath]
    bbs: list[pygame.Rect]
