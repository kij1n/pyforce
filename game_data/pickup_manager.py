from dataclasses import dataclass
from pymunk import Vec2d
from game_data.pickup import Pickup


class PickupManager:
    def __init__(self, settings, model):
        self.settings = settings
        self.model = model
        self.pickups = []
        self._load_static_pickups()

    def activate_if_in_range(self, pos: Vec2d):
        pickups_to_remove = []
        for pickup in self.pickups:
            if (pickup.pos - pos).length < self.settings["pickups"]["range"]:
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
                amount=pickup.get("amount"),
                name=pickup.get("name")
            )
            pos = Vec2d(
                pickup["position"][0], pickup["position"][1]
            )
            p = Pickup(pos, info, self._get_callback(info.type))
            self.pickups.append(p)

    def _get_callback(self, pickup_type):
        return getattr(self.model, f"pickup_{pickup_type}")


@dataclass
class PickupInfo:
    type: str
    amount: int = None
    name: str = None