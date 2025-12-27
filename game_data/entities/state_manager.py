from pymunk import Vec2d

class StateManager:
    def __init__(self, entity):
        self.entity = entity
        self.state = State('idle', self.entity.get_position())

    def get_where(self, player_pos : tuple[int, int] = None) -> tuple[tuple[int,int], str]:
        if player_pos is None:
            sprite_name = self.entity.get_sprite_name(self.state.get_state(), 0)
            return (
                self.entity.get_position()
            ), sprite_name
        # else:
        #     return (
        #         self.entity.get_position()
        #     ), self.entity.get_sprite_name(self.state, 0)

    def apply_horizontal_velocity(self, direction: str):
        if self.state.get_state() == "idle":
            self.state.change_state("run", self.entity.get_position(), self.entity)

        movement = self.entity.settings["player_info"]["move_horizontal"]

        if direction == "left":
            movement *= -1

        velocity = Vec2d(
            movement,
            self.entity.shape.body.velocity.y
        )
        self.entity.shape.body.velocity = velocity

        print(f"Applied horizontal velocity: {velocity} to entity at position {self.entity.get_position()}, propert: {self.entity.shape.body.velocity}")

class State:
    def __init__(self, state, position: Vec2d):
        self.state = state
        self.start_pos = position

    def change_state(self, new_state, position: Vec2d, entity):
        self.state = new_state
        self.start_pos = position
        entity.body.activate()

    def get_state(self):
        return self.state