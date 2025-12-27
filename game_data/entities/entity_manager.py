from .player import Player
from .enemy import Enemy

class EntityManager:
    def __init__(self, settings: dict):
        self.player = Player(settings)
        self.enemies = {
            # 'enemy1': Enemy(settings),
            # 'enemy2': Enemy(settings),
        }

    def update_ground_contact(self, entities_touching_ground: list):
        for entity in self.get_entities():
            identifier = getattr(entity.feet, 'id', None)

            # if identifier is not None:
            #     print("identifier is not none yay")

            if identifier in entities_touching_ground:
                entity.state_manager.state.set_on_ground(True)
                print("set true")
            else:
                entity.state_manager.state.set_on_ground(False)
                print("set false")

    def update_timers(self):
        for entity in self.get_entities():
            entity.state_manager.state.append_time()

    def update_entity_states(self):
        for entity in self.get_entities():
            if entity.shape.body.velocity == (0, 0) and not entity.state_manager.state.get_state() == "idle":
                entity.state_manager.state.change_state("idle", entity.get_position(), entity)

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

    def get_where(self):
        where = [self.player.state_manager.get_where()]

        for enemy in self.enemies.values():
            where.append(enemy.state_manager.get_where(player_pos=self.player.get_position()))

        return where

    def get_entities(self):
        return [
            self.player,
            # self.enemies.values()
        ]