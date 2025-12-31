import math

from shared import Where
from .player import Player
from .enemy import Enemy

class EntityManager:
    def __init__(self, settings: dict):
        self.settings = settings
        self.player = Player(settings)
        self.enemies = {
            # 'enemy1': Enemy(settings),
            # 'enemy2': Enemy(settings),
        }

    def update_player_aim(self, mouse_pos):
        # mouse pos is in relative coordinates
        # so we need to use player's rel not abs position
        player_pos = self.player.get_relative_pos()

        vector = (
            mouse_pos[0] - player_pos[0],
            mouse_pos[1] - player_pos[1]
        )
        angle = math.atan2(-vector[1], vector[0]) * (180 / math.pi)
        angle += 90  # 0 degrees must be pointing down, but Y axis is inverted in pygame
        angle = angle % 360

        self.player.arm_deg = angle

    def update_ground_contact(self, entities_touching_ground: list):
        for entity in self.get_entities():
            identifier = getattr(entity.feet, 'id', None)

            if identifier in entities_touching_ground:
                entity.state_manager.state.set_on_ground(True, entity.shape.body)
                # print('set ground contact -> True')
            else:
                entity.state_manager.state.set_on_ground(False, entity.shape.body)
                # print('set ground contact -> False')

    def update_timers(self):
        for entity in self.get_entities():
            entity.state_manager.state.append_time()

    def update_entity_states(self):
        for entity in self.get_entities():
            if (entity.shape.body.velocity == (0, 0) and
                entity.state_manager.state.is_on_ground and
                not entity.state_manager.state.get_state() == "idle"):
                entity.state_manager.state.change_state("idle", entity.get_position(), entity.shape.body)

    def move_player(self, direction: str):
        if direction in ["left", "right"]:
            self.player.state_manager.apply_horizontal_velocity(direction)
        else:
            self.player.state_manager.apply_vertical_push()

    def get_player_pos(self):
        pos = self.player.get_position()
        return (
            pos[0], pos[1]
        )

    def get_where_array(self) -> list[Where]:
        where = [self.player.state_manager.get_where()]

        for enemy in self.enemies.values():
            where.append(enemy.state_manager.get_where(player_pos=self.player.get_position()))

        return where

    def get_entities(self):
        return [
            self.player,
            # self.enemies.values()
        ]