from .physics import PhysicsEngine
from .json_manager import JSONManager
from . import entities

class Model:
    def __init__(self):
        self.settings = JSONManager()
        self.entities = entities.EntityManager(self.settings.s)
        self.physics = PhysicsEngine(self.settings.s)

    def get_center_pos(self) -> tuple[int, int]:
        player_pos = self.entities.get_player_pos()
        center_x = (
            self.settings.s["screen"]['size_x'] // 2
            if player_pos[0] < self.settings.s["screen"]['size_x'] // 2
            else player_pos[0]
        )
        return center_x, player_pos[1]