from .state_manager import StateManager
from pymunk import Body, Poly, Vec2d, ShapeFilter


class Player:
    def __init__(self, settings: dict):
        self.name = "player"
        self.settings = settings

        self._prepare_collision_box()
        self.state_manager = StateManager(self)

        self.sprite_names = {
            "idle": [
                "idle1", "idle2"
            ],
            "run": [
                "run1", "run2", "run3",
                "run4", "run5", "run6"
            ],
            "jump": [
                "jump1", "jump2",
                "jump3", "jump4"
            ]
        }

        self.arm_deg = 0 # 0 means pointing down, turns counter-clockwise
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
        return len(self.sprite_names[state])

    def _prepare_collision_box(self):
        mass = self.settings["player_info"]["mass"]
        moment = self.settings["player_info"]["moment"]

        self.body = Body(
            mass=mass,
            moment=float('inf') if moment is None else moment,
            body_type=Body.DYNAMIC
        )
        self.body.position = Vec2d(  # position of center of mass
            self.settings["player_info"]["start_x"],
            self.settings["player_info"]["start_y"]
        )

        hitbox_x = self.settings["player_info"]["hitbox_x"]
        hitbox_y = self.settings["player_info"]["hitbox_y"]
        feet_y = self.settings["player_info"]["feet_hitbox_y"]

        h_y = hitbox_y / 2
        h_x = hitbox_x / 2

        vertical_shift = self._calc_vertical_shift(
            h_y,
            -h_y - feet_y
        )

        # Body shape
        # In Pygame: Top is negative Y (-h_y), Bottom is positive Y (h_y)
        self.shape = Poly(
            self.body,
            [
                (-h_x, -h_y - vertical_shift),
                (-h_x, h_y - vertical_shift),
                (h_x, h_y - vertical_shift),
                (h_x, -h_y - vertical_shift)
            ]
        )
        self.shape.friction = self.settings["player_info"]["friction"]
        self.shape.collision_type = self.settings["physics"]["collision_types"]["player"]

        self.shape.filter = ShapeFilter(
            categories=self.settings["physics"]["collision_categories"]['player'],
            mask=self.settings["physics"]["collision_masks"]['player']
        )

        self.feet = Poly(
            self.body,
            [
                (-h_x, h_y - vertical_shift),
                (-h_x, h_y + feet_y - vertical_shift),
                (h_x, h_y + feet_y - vertical_shift),
                (h_x, h_y - vertical_shift)
            ]
        )
        self.feet.friction = self.settings["player_info"]["feet_friction"]
        self.feet.collision_type = self.settings["physics"]["collision_types"]["player_feet"]
        self.feet.id = self.settings["player_info"]["id"]
        self.feet.filter = ShapeFilter(
            categories=self.settings["physics"]["collision_categories"]['player_feet'],
            mask=self.settings["physics"]["collision_masks"]['player_feet']
        )

    @staticmethod
    def _calc_vertical_shift(a, b):
        # formula: a + x = -(b + x)
        # this equation ensures the center of mass is in (0,0)
        # where <a,b> is the range of y values of the hitbox
        return (a + b) / (-2)

    def get_collision_box(self):
        return [self.body, self.shape, self.feet]

    def get_sprite_name(self, state, index):
        sprite_name = self.name + "_" + self.sprite_names[state][index]
        return sprite_name

    def get_position(self) -> Vec2d:
        return self.shape.body.position

    def get_state(self):
        return self.state_manager.state

    def get_gun_position(self):
        return self.shape.body.position