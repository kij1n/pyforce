from loguru import logger
from pymunk import Vec2d
from shared import StateName, Direction


class State:
    def __init__(self, state, position: Vec2d, state_manager):
        self.state_manager = state_manager
        self.settings = state_manager.entity.settings

        self.state = state
        self.start_pos = position
        self.dead = False

        self.start_time = 0
        self.current_time = 0
        self.death_time = self.settings['sprites']['cycle_lengths'][self.state_manager.name]['death_time']
        self.wait_after_death = self.settings['sprites']['cycle_lengths'][self.state_manager.name]['wait_after_death']

        self.start_y = None
        self.highest_y = None
        self.achieved_highest_y = False

        self.movement_direction = None
        self.is_on_ground = False

    def is_inverted(self):
        return True if self.movement_direction == Direction.LEFT else False

    def can_jump(self, body) -> bool:
        return self.is_on_ground and body.velocity.y >= 0

    def set_on_ground(self, is_on_ground: bool):
        self.is_on_ground = is_on_ground

    def get_sprite_index(self, current_position: Vec2d, total_sprites: int, cycle_length: float,
                         velocity: Vec2d) -> int:
        if total_sprites <= 1:
            logger.debug("Invalid total sprites")
            return 0

        if self.state == StateName.RUN:
            return self._handle_run(current_position, total_sprites, cycle_length)
        elif self.state == StateName.IDLE:
            return self._handle_idle(cycle_length, total_sprites)
        elif self.state == StateName.JUMP:
            return self._handle_jump(current_position, total_sprites, velocity)
        elif self.state == StateName.DEATH:
            return self._handle_death(total_sprites)

        return 0

    def _handle_death(self, total_sprites):
        if self.current_time >= self.death_time:
            self.dead = True
            return total_sprites - 1

        step = self.death_time // total_sprites
        return int(self.current_time // step)

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
        if self.state in [StateName.IDLE, StateName.DEATH]:
            self.current_time += 1

    def set_direction(self, direction, position=None):
        if direction != self.movement_direction:
            self.movement_direction = direction
            self.start_pos = position

    def change_state(self, new_state, position: Vec2d, body, settings=None):
        if self.state_manager.name != 'player':
            logger.debug(f"Entity {self.state_manager.name} changing state from {self.state} to {new_state}")
        self.state = new_state

        if new_state == StateName.RUN:
            self.start_pos = position

        elif new_state == StateName.IDLE or new_state == StateName.DEATH:
            self.start_time = 0
            self.current_time = 0

        elif new_state == StateName.JUMP:
            if self.state_manager.name != 'player':
                self.start_pos = position
            self.achieved_highest_y = False
            self.start_y = position.y
            self.highest_y = self._calc_highest_y(position.y, settings)

        body.activate()

    @staticmethod
    def _calc_highest_y(current_y, settings):
        J = settings["physics"]["ent_jump_force"]
        g = settings["physics"]["gravity"]
        m = settings["player_info"]["mass"]
        y_0 = current_y
        highest_y = abs(J ** 2 / (2 * g * m ** 2) - y_0)
        return highest_y

    def get_state(self) -> StateName:
        # settings = self.get_ent_sp_settings()
        # if settings.get(self.state.value) is None:
        #     return StateName.RUN
        # else:
        #     return self.state
        return self.state

    def get_state_incl_jump(self) -> StateName:
        return self.state

    def get_ent_sp_settings(self):
        if self.state_manager.name == 'player':
            return self.settings['player_info']['sprites_paths']
        else:
            return self.settings['enemy_info'][self.state_manager.name]['sprites_paths']

    def get_state_str(self) -> str:
        return self.state.value

