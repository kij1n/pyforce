from pymunk import Vec2d
from enum import Enum
from shared import Where


class StateManager:
    def __init__(self, entity):
        self.entity = entity
        self.state = State('idle', self.entity.get_position())

        name = getattr(self.entity.name, 'value', 'player')
        if name == 'player':
            self.movement = self.entity.settings['player_info']['move_horizontal']
        else:
            self.movement = self.entity.settings['enemy_info'][name]['move_horizontal']

    def get_where(self, player_pos: tuple[int, int] = None) -> Where:
        # if player_pos is None:
        where = Where(
            position=self.entity.get_position(),
            name=getattr(self.entity.name, 'value', 'player'),
            sprite_index=self.state.get_sprite_index(
                self.entity.get_position(),
                self.entity.get_sprite_qty(self.state.get_state()),
                self.entity.settings['sprites']['cycle_lengths'][getattr(self.entity.name, 'value', 'player')][self.state.get_state()],
                self.entity.shape.body.velocity,
            ),
            state=self.state.get_state(),
            inversion=True if self.state.is_inverted() else False,
            arm_deg=getattr(self.entity, 'arm_deg', None),
            gun_name=getattr(self.entity, 'gun_held', None)
        )

        return where
        # return None

    def apply_vertical_push(self):
        # enemies will not jump, so this is only for player
        if not self.state.can_jump(self.entity.shape.body):
            return

        if self.state.get_state() != "jump":
            self.state.change_state("jump", self.entity.get_position(), self.entity.shape.body,
                                    settings=self.entity.settings)

        force = Vec2d(
            0, -self.entity.settings["player_info"]["jump_force"]
        )
        self.entity.shape.body.apply_impulse_at_local_point(force)

    def apply_horizontal_velocity(self, direction: str):
        if self._should_run():
            self.state.change_state("run", self.entity.get_position(), self.entity.shape.body)

        if direction == "left":
            self.state.set_direction(Direction.LEFT, position=self.entity.get_position())
        else:
            self.state.set_direction(Direction.RIGHT, position=self.entity.get_position())

        self._calc_and_apply_velocity()

    def _should_run(self):
        return (
            self.state.get_state() != "run" and
            self.entity.shape.body.velocity.y == 0 and
            self.state.is_on_ground
        )

    def move_along_patrol_path(self):
        pass

    def move_to_player(self):
        pass

    def _calc_and_apply_velocity(self):
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

    def get_sprite_index(self, current_position: Vec2d, total_sprites: int, cycle_length: float,
                         velocity: Vec2d) -> int:
        if total_sprites <= 1:
            return 0

        if self.state == "run":
            return self._handle_run(current_position, total_sprites, cycle_length)
        elif self.state == "idle":
            return self._handle_idle(cycle_length, total_sprites)
        elif self.state == "jump":
            return self._handle_jump(current_position, total_sprites, velocity)

        return 0

    def _handle_run(self, current_position, total_sprites, cycle_length):
        current_x = current_position.x
        start_x = self.start_pos.x

        distance_moved = abs(current_x - start_x)
        full_cycle = cycle_length * total_sprites
        rest_of_dist = distance_moved % full_cycle

        return int(rest_of_dist // cycle_length)

    def _handle_idle(self, cycle_length, total_sprites):
        time_elapsed = self.current_time - self.start_time
        full_cycle = cycle_length * total_sprites
        rest_of_time = time_elapsed % full_cycle

        return int(rest_of_time // cycle_length)

    def _handle_jump(self, current_position, total_sprites, velocity):
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

        if not self.achieved_highest_y:
            return index
        else:
            index = self._reverse_index(index, total_sprites)
            return index

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
        highest_y = abs(J ** 2 / (2 * g * m ** 2) - y_0)
        return highest_y

    def get_state(self):
        return self.state


class Direction(Enum):
    LEFT = 'left'
    RIGHT = 'right'
