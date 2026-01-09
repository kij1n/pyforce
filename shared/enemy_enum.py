from enum import Enum

class SkinColor(Enum):
    GROUND = 1
    FLYING = 2

class EnemyName(Enum):
    SKELETON = 'skeleton'
    GOBLIN = 'goblin'

def get_enemy_name(name) -> EnemyName:
    return EnemyName(name)