from .state_manager import StateManager
from pymunk import Body, Poly

class Player:
    def __init__(self, settings : dict):
        self.name = "player"
        self.position = (
            settings["player_info"]["start_x"],
            settings["player_info"]["start_y"]
        )
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
            ]
        }

    def get_sprite_name(self, state, index):
        sprite_name = self.name + "_" + self.sprite_names[state][index]
        return sprite_name

    def get_position(self):
        return self.position

    def move(self, direction: str):
        match direction:
            case "left":
                self.position = (
                    self.position[0] - self.movement_speed,
                    self.position[1]
                )
            case "right":
                self.position = (
                    self.position[0] + self.movement_speed,
                    self.position[1]
                )

    def get_state(self):
        return self.state_manager.state
