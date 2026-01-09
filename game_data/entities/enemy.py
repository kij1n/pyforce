from .state_manager import StateManager
from shared import SkinColor, EnemyName
from .entity_helper import prepare_collision_box

class Enemy:
    def __init__(self, name: EnemyName, skin_color: SkinColor, settings : dict):
        self.name = name
        self.skin_color = skin_color  # flying or ground
        self.settings = settings
        self.state_manager = StateManager(self)
        self.body, self.shape, self.feet = prepare_collision_box(name.value, settings)

    def get_sprite_qty(self, state):
        return len(self.settings["enemy_info"][self.name]["sprites_paths"][state])