from .physics import PhysicsEngine
from .json_manager import JSONManager
from . import entities

class Model:
    def __init__(self):
        self.settings = JSONManager()
        self.entities = entities.EntityManager()

    def get_center_pos(self):
        pass