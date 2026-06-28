from dataclasses import dataclass

@dataclass
class PickupInfo:
    type: str
    movement_range: tuple[int, int]
    movement_speed: float
    amount: int = None
    name: str = None
