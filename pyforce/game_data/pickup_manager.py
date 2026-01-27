import weakref
from dataclasses import dataclass
from pymunk import Vec2d
from .pickup import Pickup


class PickupManager:
    def __init__(self, settings, model):
        self.settings = settings
        self.model = weakref.proxy(model)
        self.pickups = []
        self._load_static_pickups()

    def activate_if_in_range(self, pos: Vec2d):
        pickups_to_remove = []
        for pickup in self.pickups:
            if (pickup.pos - pos).length < self.settings["pickups"]["settings"]["range"]:
                pickup.activate()
                pickups_to_remove.append(pickup)
        for pickup in pickups_to_remove:
            self.pickups.remove(pickup)

    def get_pickups(self):
        return self.pickups

    def _load_static_pickups(self):
        for pickup in self.settings["pickups"]["static"]:
            info = PickupInfo(
                type=pickup["type"],
                movement_range=self.settings["pickups"]["settings"]["movement_range"],
                amount=pickup.get("amount"),
                name=pickup.get("name"),
                movement_speed=self.settings["pickups"]["settings"]["movement_speed"]
            )
            pos = Vec2d(
                pickup["position"][0], pickup["position"][1]
            )
            p = Pickup(pos, info, self._get_callback(info.type))
            self.pickups.append(p)

    def _get_callback(self, pickup_type):
        return getattr(self.model, f"pickup_{pickup_type}")

    def update_pickups_pos(self, dt):
        for pickup in self.pickups:
            pickup.update_pos(dt)


@dataclass
class PickupInfo:
    type: str
    movement_range: tuple[int, int]
    movement_speed: float
    amount: int = None
    name: str = None