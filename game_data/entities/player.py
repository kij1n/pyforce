from .state_manager import StateManager
from pymunk import Body, Poly, Vec2d

class Player:
    def __init__(self, settings : dict):
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
                "jump1", "jump2"
                "jump3", "jump4"
            ]
        }

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
            hitbox_y / 2,
            -hitbox_y / 2 - feet_y
        )

        # main body shape
        self.shape = Poly(
            self.body,
            [  # vertices relative to center of mass
                (-h_x, h_y + vertical_shift),
                (-h_x, -h_y + vertical_shift),
                (h_x, -h_y + vertical_shift),
                (h_x, h_y + vertical_shift)
            ]
        )
        self.shape.friction = self.settings["player_info"]["friction"]



        # feet shape to allow better horizontal movement on ground
        self.feet = Poly(
            self.body,
            [
                (-h_x, -h_y + vertical_shift),
                (-h_x, -h_y - feet_y + vertical_shift),
                (h_x, -h_y - feet_y + vertical_shift),
                (h_x, -h_y + vertical_shift)
            ]
        )
        self.feet.friction = self.settings["player_info"]["feet_friction"]

    @staticmethod
    def _calc_vertical_shift(a, b):
        # formula: a + x = -(b + x)
        # this equation ensures the center of mass is in (0,0)
        # where <a,b> is the range of y values of the hitbox
        return  (a+b) / (-2)

    def get_collision_box(self):
        return [self.body, self.shape, self.feet]

    def get_sprite_name(self, state, index):
        sprite_name = self.name + "_" + self.sprite_names[state][index]
        return sprite_name

    def get_position(self) -> Vec2d:
        return self.shape.body.position

    def get_state(self):
        return self.state_manager.state
