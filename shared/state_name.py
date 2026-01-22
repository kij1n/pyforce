"""
This module defines the StateName enum for entity animation states.
"""
from enum import Enum


class StateName(Enum):
    """
    Enum representing various animation and behavioral states of an entity.
    Notice that both the player and enemies have their own states. The player
    cannot be in attack state.

    Attributes:
        IDLE (str): Entity is in an idle state.
        RUN (str): Entity is running or moving.
        JUMP (str): Entity is jumping.
        DEATH (str): Entity is in a death state or animation.
        ATTACK (str): Entity is performing an attack.
    """
    IDLE = "idle"
    RUN = "run"
    JUMP = "jump"
    DEATH = "death"
    ATTACK = "attack"
