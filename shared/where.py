from dataclasses import dataclass

@dataclass
class Where:
    position: tuple[int, int]
    name: str
    state: str
    sprite_index: int
    inversion: bool
    arm_deg: int
    gun_name: str