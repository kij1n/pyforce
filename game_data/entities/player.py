from .state_manager import StateManager
from .entity_helper import prepare_collision_box
from pymunk import Vec2d


class Player:
    def __init__(self, settings: dict):
        self.name = "player"
        self.settings = settings
        self.health = 100

        self.body, self.shape, self.feet = prepare_collision_box(self.name, settings, self)
        self.state_manager = StateManager(self)

        self.arm_deg = 0  # 0 means pointing down, turns counter-clockwise
        self.gun_held = 'base'
        self.ammo_used = 'base'

    def get_relative_pos(self):
        player_abs_pos = self.get_position()

        screen_w = self.settings['screen']['size_x']
        screen_h = self.settings['screen']['size_y']
        map_w = self.settings['map']['size_x']
        map_h = self.settings['map']['size_y']

        # Calculate where the camera wants to be (centered on player)
        # Camera Top-Left = Player Center - Half Screen
        cam_x = player_abs_pos[0] - (screen_w // 2)
        cam_y = player_abs_pos[1] - (screen_h // 2)

        # Clamp the camera so it doesn't show outside the map
        cam_x = max(0, min(cam_x, map_w - screen_w))
        cam_y = max(0, min(cam_y, map_h - screen_h))

        # Relative Position = Absolute Position - Camera Position
        return player_abs_pos[0] - cam_x, player_abs_pos[1] - cam_y

    def get_sprite_qty(self, state):
        return len(self.settings["player_info"]["sprites_paths"][state])

    def get_collision_box(self):
        return [self.body, self.shape, self.feet]

    def get_position(self) -> Vec2d:
        return self.shape.body.position

    def get_state(self):
        return self.state_manager.state

    def get_gun_position(self):
        return self.shape.body.position
