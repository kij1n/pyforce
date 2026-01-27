"""
This module contains enums and utilities related to enemy identification and actions.
"""
from enum import Enum


class EnemyName(Enum):
    """
    Enum representing the names of different enemy types.
    """
    SKELETON = "skeleton"
    GOBLIN = "goblin"


class EnemyAction(Enum):
    """
    Enum representing the possible actions or behaviors of an enemy.

    Attributes:
        AGGRO (str): Enemy is aggressive and actively pursuing the player.
        PATROL (str): Enemy is patrolling a designated path.
        IDLE (str): Enemy is standing still.
        ATTACK (str): Enemy is performing an attack.
        DEATH (str): Enemy is in the death state.
    """
    AGGRO = "aggro"
    PATROL = "patrol"
    IDLE = "idle"
    ATTACK = "attack"
    DEATH = "death"


def get_enemy_name(name) -> EnemyName:
    """
    Converts a string to its corresponding EnemyName enum value.

    :param name: The name of the enemy as a string.
    :return: The matching EnemyName enum member.
    """
    return EnemyName(name)
