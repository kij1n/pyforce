from enum import Enum


class StateName(Enum):
    IDLE = "idle"
    RUN = "run"
    JUMP = "jump"
    DEATH = "death"
    ATTACK = "attack"
