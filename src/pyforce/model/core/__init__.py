"""
This module initializes the game_data package and exports the Model class.
"""

from .model import Model
from .effects_manager import EffectsManager
from .particle import Particle
from .physics import PhysicsEngine
from .pickup_manager import PickupManager, PickupInfo
from .pickup import Pickup

__all__ = ["Model", "EffectsManager", "Particle", "PhysicsEngine", "PickupManager", "PickupInfo", "Pickup"]
