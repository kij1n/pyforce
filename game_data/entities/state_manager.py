from pymunk import Vec2d
from enum import Enum
from shared import Where


class StateManager:
    def __init__(self, entity):
        self.entity = entity
        self.state = State('idle', self.entity.get_position())
        self.movement = self.entity.settings["player_info"]["move_horizontal"]


    def get_where(self, player_pos : tuple[int, int] = None) -> Where:
        if player_pos is None:
            # sprite_index = self.state.get_sprite_index(
            #     self.entity.get_position(),
            #     self.entity.get_sprite_qty(self.state.get_state()),
            #     self.entity.settings["sprites"]["cycle_lengths"]["player"][self.state.get_state()]
            # )
            #
            # sprite_name = self.entity.get_sprite_name(self.state.get_state(), sprite_index)
            #
            # if self.state.movement_direction == Direction.LEFT:
            #     inv_indicator = self.entity.settings["sprites"]["inversion_indicator"]
            #     sprite_name = inv_indicator + sprite_name
            #
            # arm_separator = self.entity.settings["sprites"]["arm_separator"]
            # sprite_name = sprite_name + arm_separator + str(self.arm_deg)

            # return (
            #     self.entity.get_position()
            # ), sprite_name
            #

            where = Where(
                position=self.entity.get_position(),
                name=self.entity.name,
                sprite_index=self.state.get_sprite_index(
                    self.entity.get_position(),
                    self.entity.get_sprite_qty(self.state.get_state()),
                    self.entity.settings['sprites']['cycle_lengths']['player'][self.state.get_state()],
                    self.entity.shape.body.velocity,
                ),
                state=self.state.get_state(),
                inversion=True if self.state.is_inverted() else False,
                arm_deg=getattr(self.entity, 'arm_deg', None),
                gun_name=getattr(self.entity, 'gun_held', None)
            )

            return where
        return None

    def apply_vertical_push(self):
        # enemies will not jump, so this is only for player
        if not self.state.can_jump(self.entity.shape.body):
            return

        if self.state.get_state() != "jump":
            self.state.change_state("jump", self.entity.get_position(), self.entity.shape.body, settings=self.entity.settings)

        force = Vec2d(
            0,
            -self.entity.settings["player_info"]["jump_force"]
        )
        self.entity.shape.body.apply_impulse_at_local_point(force)

    def apply_horizontal_velocity(self, direction: str):
        if self.state.get_state() != "run" and self.entity.shape.body.velocity.y == 0 and self.state.is_on_ground:
            self.state.change_state("run", self.entity.get_position(), self.entity.shape.body)

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

        self.start_y = None
        self.highest_y = None
        self.achieved_highest_y = False

        self.movement_direction = None
        self.is_on_ground = False

    def is_inverted(self):
        return True if self.movement_direction == Direction.LEFT else False

    def can_jump(self, body) -> bool:
        return self.is_on_ground and body.velocity.y >= 0

    def set_on_ground(self, is_on_ground: bool, body):
        self.is_on_ground = is_on_ground
        # if is_on_ground:
        #     if body.velocity.x != 0:
        #         self.change_state("run", body.position, body)
        #     else:
        #         self.change_state("idle", body.position, body)

    def get_sprite_index(self, current_position: Vec2d, total_sprites: int, cycle_length: float, velocity: Vec2d) -> int:
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
        elif self.state == "jump":
            current_y = current_position.y
            end_y = self.highest_y

            h_total_sprites = int(total_sprites // 2)

            if (current_y <= end_y or velocity.y > 0) and not self.achieved_highest_y:
                self.achieved_highest_y = True
                return h_total_sprites - 1

            current_dist = abs(self.start_y - current_y)
            total_dist = abs(end_y - self.start_y)

            cycle_length = total_dist / h_total_sprites

            if current_dist >= total_dist:
                index = 0
            else:
                index = int(current_dist // cycle_length)

            # debug
            # print(f"current_dist {current_dist} total_dist: {total_dist} index: {
            # index if not self.achieved_highest_y else self._reverse_index(index + h_total_sprites, total_sprites)
            # }, achieved_highest_y: {self.achieved_highest_y}")

            if not self.achieved_highest_y:
                return index
            else:
                index = self._reverse_index(index, total_sprites)
                return index

        return 0

    @staticmethod
    def _reverse_index(index, total_sprites):
        return total_sprites - 1 - index

    def append_time(self):
        if self.state == "idle":
            self.current_time += 1

    def set_direction(self, direction, position=None):
        if direction != self.movement_direction:
            self.movement_direction = direction
            self.start_pos = position

    def change_state(self, new_state, position: Vec2d, body, settings=None):
        # print(f"{self.state} -> {new_state}")
        self.state = new_state

        if new_state == "run":
            self.start_pos = position

        elif new_state == "idle":
            self.start_time = 0
            self.current_time = 0

        elif new_state == "jump":
            self.achieved_highest_y = False
            self.start_y = position.y
            self.highest_y = self._calc_highest_y(position.y, settings)

        body.activate()

    @staticmethod
    def _calc_highest_y(current_y, settings):
        J = settings["player_info"]["jump_force"]
        g = settings["physics"]["gravity"]
        m = settings["player_info"]["mass"]
        y_0 = current_y
        highest_y = abs(J**2 / (2*g*m**2) - y_0)
        return highest_y

    def get_state(self):
        return self.state

class Direction(Enum):
    LEFT = -1
    RIGHT = 1