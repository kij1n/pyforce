from .state_manager import StateManager
from shared import SkinColor, EnemyName
from .entity_helper import prepare_collision_box

class Enemy:
    def __init__(self, name: EnemyName, skin_color: SkinColor, settings : dict, pos, ent_id):
        self.name = name
        self.skin_color = skin_color  # flying or ground
        self.settings = settings
        self.body, self.shape, self.feet = prepare_collision_box(name.value, settings, pos, ent_id=ent_id)
        self.state_manager = StateManager(self)

    def get_sprite_qty(self, state):
        return len(self.settings["enemy_info"][self.name.value]["sprites_paths"][state])

    def get_position(self):
        return self.shape.body.position

    def get_collision_box(self):
        return [self.body, self.shape, self.feet]