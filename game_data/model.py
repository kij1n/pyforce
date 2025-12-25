from .physics import PhysicsEngine
from . import entities

class Model:
    def __init__(self, settings: dict):
        self.settings = settings

        self.entities = entities.EntityManager(self.settings)
        self.physics = PhysicsEngine(self.settings)

        self.where = self._create_where()

    def update(self):


        self.where = self.entities.get_where()

    def get_center_pos(self) -> tuple[int, int]:
        player_pos = self.entities.get_player_pos()
        center_x = (
            self.settings["screen"]['size_x'] // 2
            if player_pos[0] < self.settings["screen"]['size_x'] // 2
            else player_pos[0]
        )
        return center_x, player_pos[1]

    def get_where(self) -> dict:
        return self.where

    def _create_where(self) -> dict:
        return self.entities.get_where()