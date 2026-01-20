from shared import Where, DebugElements
from .physics import PhysicsEngine
from . import entities
from loguru import logger


class Model:
    def __init__(self, settings: dict):
        logger.info("Initializing model...")

        self.settings = settings

        self.physics = PhysicsEngine(self.settings)
        self.entities = entities.EntityManager(self.settings, self.physics.sim)
        self.insert_ents_to_sim()

        self.where_array = self._create_where()
        self.debug_elements = DebugElements(None, None, None)

    def game_not_lost(self):
        return self.entities.player is not None

    def update(self, mouse_pos):
        self.entities.update_entity_states()
        self.entities.update_timers()
        self.entities.update_ground_contact(self.physics.entities_touching_ground)
        self.entities.update_enemy_action(self.physics.sim)
        self.entities.update_player_aim(mouse_pos)
        self.entities.update_bullets()

        self.where_array = self.entities.get_where_array()

        self.physics.sim.step(self.settings["physics"]["time_step"])
        self.entities.handle_hits(self.physics.entities_hit, self.physics.sim)

        self._add_debug()

    def _add_debug(self):
        self.debug_elements = DebugElements(self.physics.sim, self.entities.patrol_paths, self._add_bbs())

    def _add_bbs(self):
        bbs = []
        if self.settings["debug"]["show_bbs"]:

            for i in self.where_array:
                bbs.append(i.hitbox)
        return bbs

    def get_center_pos(self) -> tuple[int, int]:
        player_pos = self.entities.get_player_pos()
        return player_pos

    def get_where_array(self) -> list[Where]:
        return self.where_array

    def get_bullets_dict(self):
        return self.entities.bullets_dict

    def _create_where(self):
        return self.entities.get_where_array()

    def insert_ents_to_sim(self):
        ents = self.entities.get_entities()
        for ent in ents:
            body, shape, feet = ent.get_collision_box()
            self.physics.sim.add(body, shape, feet)

    def move_player(self, direction: str):
        self.entities.move_player(direction)

    def player_shoot(self):
        body, shape, bullet = self.entities.get_bullet()

        if body is None or shape is None or bullet is None:
            return

        self.physics.sim.add(body, shape)
        self.entities.bullets_dict[bullet] = shape
