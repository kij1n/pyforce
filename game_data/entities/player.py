from .state_manager import StateManager
from pymunk import Body, Poly, Vec2d, ShapeFilter


class Player:
    def __init__(self, settings: dict):
        self.name = "player"
        self.settings = settings

        self._prepare_collision_box()
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

    def _prepare_collision_box(self):
        mass = self.settings["player_info"]["mass"]
        moment = self.settings["player_info"]["moment"]

        self.body = self._create_body(mass, moment, self.settings)
        self.shape = self._create_shape(self.body, self.settings)
        self.feet = self._create_feet(self.body, self.settings)

    @staticmethod
    def _create_body(mass, moment, settings):
        body = Body(
            mass=mass,
            moment=float('inf') if moment is None else moment,
            body_type=Body.DYNAMIC
        )
        body.position = Vec2d(  # position of the center of mass
            settings["player_info"]["start_x"],
            settings["player_info"]["start_y"]
        )
        return body

    def _create_shape(self, body, settings):
        h_x = settings["player_info"]["hitbox_x"] // 2
        h_y = settings["player_info"]["hitbox_y"] // 2
        feet_y = settings["player_info"]["feet_hitbox_y"]

        vertical_shift = self._calc_vertical_shift(
            h_y,
            -h_y - feet_y
        )

        # in pygame: Top is negative Y (-h_y), Bottom is positive Y (h_y)
        shape = Poly(
            body,
            [
                (-h_x, -h_y - vertical_shift),
                (-h_x, h_y - vertical_shift),
                (h_x, h_y - vertical_shift),
                (h_x, -h_y - vertical_shift)
            ]
        )
        shape.friction = settings["player_info"]["friction"]
        shape.collision_type = settings["physics"]["collision_types"]["player"]

        shape.filter = ShapeFilter(
            categories=settings["physics"]["collision_categories"]['player'],
            mask=settings["physics"]["collision_masks"]['player']
        )
        return shape

    def _create_feet(self, body, settings):
        h_x = settings["player_info"]["hitbox_x"] // 2
        h_y = settings["player_info"]["hitbox_y"] // 2
        feet_y = settings["player_info"]["feet_hitbox_y"]

        vertical_shift = self._calc_vertical_shift(
            h_y,
            -h_y - feet_y
        )

        feet = Poly(
            body,
            [
                (-h_x, h_y - vertical_shift),
                (-h_x, h_y + feet_y - vertical_shift),
                (h_x, h_y + feet_y - vertical_shift),
                (h_x, h_y - vertical_shift)
            ]
        )
        feet.friction = settings["player_info"]["feet_friction"]
        feet.collision_type = settings["physics"]["collision_types"]["player_feet"]
        feet.id = settings["player_info"]["id"]

        feet.filter = ShapeFilter(
            categories=self.settings["physics"]["collision_categories"]['player_feet'],
            mask=self.settings["physics"]["collision_masks"]['player_feet']
        )

        return feet


    @staticmethod
    def _calc_vertical_shift(a, b):
        # formula: a + x = -(b + x)
        # this equation ensures the center of mass is in (0,0)
        # where <a,b> is the range of y values of the hitbox
        return (a + b) / (-2)

    def get_collision_box(self):
        return [self.body, self.shape, self.feet]

    def get_position(self) -> Vec2d:
        return self.shape.body.position

    def get_state(self):
        return self.state_manager.state

    def get_gun_position(self):
        return self.shape.body.position
