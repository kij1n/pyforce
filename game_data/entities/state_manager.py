from pymunk import Vec2d
from enum import Enum

class StateManager:
    def __init__(self, entity):
        self.entity = entity
        self.state = State('idle', self.entity.get_position())
        self.movement = self.entity.settings["player_info"]["move_horizontal"]

    def get_where(self, player_pos : tuple[int, int] = None) -> tuple[tuple[int,int], str]:
        if player_pos is None:
            sprite_index = self.state.get_sprite_index(
                self.entity.get_position(),
                self.entity.get_sprite_qty(self.state.get_state()),
                self.entity.settings["sprites"]["cycle_lengths"]["player"][self.state.get_state()]
            )

            sprite_name = self.entity.get_sprite_name(self.state.get_state(), sprite_index)

            if self.state.movement_direction == Direction.LEFT:
                inv_indicator = self.entity.settings["sprites"]["inversion_indicator"]
                sprite_name = inv_indicator + sprite_name

            return (
                self.entity.get_position()
            ), sprite_name
        return None

    def apply_vertical_push(self):
        # enemies will not jump, so this is only for player
        if not self.state.can_jump():
            return

        if self.state.get_state() == "idle":
            self.state.change_state("jump", self.entity.get_position(), self.entity)

        force = Vec2d(
            0,
            -self.entity.settings["player_info"]["jump_force"]
        )
        self.entity.shape.body.apply_impulse_at_local_point(force)

    def apply_horizontal_velocity(self, direction: str):
        if self.state.get_state() == "idle" and not self.state.get_state() == "jump":
            self.state.change_state("run", self.entity.get_position(), self.entity)

        if direction == "left":
            self.state.set_direction(Direction.LEFT, position=self.entity.get_position())
        else:
            self.state.set_direction(Direction.RIGHT, position=self.entity.get_position())

        velocity = Vec2d(
            self.movement if self.state.movement_direction == Direction.RIGHT else -self.movement,
            self.entity.shape.body.velocity.y
        )
        self.entity.shape.body.velocity = velocity

class State:
    def __init__(self, state, position: Vec2d):
        self.state = state
        self.start_pos = position
        self.start_time = 0
        self.current_time = 0
        self.movement_direction = None
        self.is_on_ground = False

    def can_jump(self) -> bool:
        return self.is_on_ground

    def set_on_ground(self, is_on_ground: bool):
        self.is_on_ground = is_on_ground

    def get_sprite_index(self, current_position: Vec2d, total_sprites: int, cycle_length: float) -> int:
        if total_sprites <= 1:
            return 0

        if self.state == "run":
            current_x = current_position.x
            start_x = self.start_pos.x

            distance_moved = abs(current_x - start_x)
            full_cycle = cycle_length * total_sprites
            rest_of_dist = distance_moved % full_cycle

            return int(rest_of_dist // cycle_length)
        elif self.state == "idle":
            time_elapsed = self.current_time - self.start_time
            full_cycle = cycle_length * total_sprites
            rest_of_time = time_elapsed % full_cycle

            return int(rest_of_time // cycle_length)
        return 0

    def append_time(self):
        if self.state == "idle":
            self.current_time += 1

    def set_direction(self, direction, position=None):
        if direction != self.movement_direction:
            self.movement_direction = direction
            self.start_pos = position

    def change_state(self, new_state, position: Vec2d, entity):
        self.state = new_state
        self.start_pos = position

        self.start_time = 0
        self.current_time = 0

        entity.body.activate()

    def get_state(self):
        return self.state

class Direction(Enum):
    LEFT = -1
    RIGHT = 1