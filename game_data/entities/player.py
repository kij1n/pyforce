from .state_manager import StateManager
from pymunk import Body, Poly, Vec2d

class Player:
    def __init__(self, settings : dict):
        self.name = "player"
        self.settings = settings

        self._prepare_collision_box()

        self.state_manager = StateManager(self)

        self.movement_speed = settings["player_info"]["movement_speed"]

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
            moment=moment,
            body_type=Body.DYNAMIC
        )
        self.body.position = Vec2d(
            self.settings["player_info"]["start_x"],
            self.settings["player_info"]["start_y"]
        )
        self.shape = Poly(
            self.body,
            [
                (0,0),
                (0, self.settings["player_info"]["hitbox_y"]),
                (self.settings["player_info"]["hitbox_x"], self.settings["player_info"]["hitbox_y"]),
                (self.settings["player_info"]["hitbox_x"], 0)
            ]
        )


    def get_collision_box(self):
        return [self.body, self.shape]

    def get_sprite_name(self, state, index):
        sprite_name = self.name + "_" + self.sprite_names[state][index]
        return sprite_name

    def get_position(self) -> Vec2d:
        return self.shape.body.position

    def get_state(self):
        return self.state_manager.state
