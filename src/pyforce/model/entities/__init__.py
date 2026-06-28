"""
This module initializes the entities package and exports the EntityManager class.
"""

from .entity_manager import EntityManager
from .player import Player

__all__ = ["EntityManager", "Player"]
