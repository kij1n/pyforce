from .state_manager import StateManager

class Player:
    def __init__(self, settings : dict):
        self.position = (
            settings["player_info"]["start_x"],
            settings["player_info"]["start_y"]
        )
        self.state_manager = StateManager(self)

        self.movement_speed = settings["player_info"]["movement_speed"]

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