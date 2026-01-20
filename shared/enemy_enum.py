from enum import Enum


class EnemyName(Enum):
    SKELETON = "skeleton"
    GOBLIN = "goblin"


class EnemyAction(Enum):
    AGGRO = "aggro"
    PATROL = "patrol"
    IDLE = "idle"
    ATTACK = "attack"
    DEATH = "death"


def get_enemy_name(name) -> EnemyName:
    return EnemyName(name)
