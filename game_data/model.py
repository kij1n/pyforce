from shared import Where
from .physics import PhysicsEngine
from . import entities

class Model:
    def __init__(self, settings: dict):
        self.settings = settings

        self.entities = entities.EntityManager(self.settings)
        self.physics = PhysicsEngine(self.settings)
        self.insert_ents_to_sim()

        self.where_array = self._create_where()

    def update(self, mouse_pos):
        self.entities.update_entity_states()
        self.entities.update_timers()
        self.entities.update_ground_contact(self.physics.entities_touching_ground)
        self.entities.update_player_aim(mouse_pos)

        self.where_array = self.entities.get_where_array()

        self.physics.sim.step(self.settings["physics"]['time_step'])

    def get_center_pos(self) -> tuple[int, int]:
        player_pos = self.entities.get_player_pos()
        return player_pos

    def get_where_array(self) -> list[Where]:
        return self.where_array

    def _create_where(self):
        return self.entities.get_where_array()

    def insert_ents_to_sim(self):
        ents = self.entities.get_entities()
        for ent in ents:
            body, shape, feet = ent.get_collision_box()
            self.physics.sim.add(body, shape, feet)

    def move_player(self, direction: str):
        self.entities.move_player(direction)