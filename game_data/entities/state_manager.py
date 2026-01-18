from loguru import logger
from pymunk import Vec2d
from shared import *
from .state import *
from .entity_utils import get_ent_rect


class StateManager:
    def __init__(self, entity):
        self.entity = entity

        self.name = getattr(self.entity.name, 'value', 'player')
        if self.name == 'player':
            self.movement = self.entity.settings['player_info']['move_horizontal']
        else:
            self.movement = self.entity.settings['enemy_info'][self.name]['move_horizontal']

        self.state = State(
            StateName.IDLE,
            self.entity.get_position(),
            self
        )

    def get_where(self, player_pos: tuple[int, int] = None) -> Where:
        # if player_pos is None:
        where = Where(
            position=self.entity.get_position(),
            name=getattr(self.entity.name, 'value', 'player'),
            sprite_index=self.state.get_sprite_index(
                self.entity.get_position(),
                self.entity.get_sprite_qty(self.state.get_state_str()),
                self.entity.settings['sprites']['cycle_lengths'][self.name].get(self.state.get_state_str(), None),
                self.entity.shape.body.velocity,
            ),
            state=self.state.get_state(),
            inversion=True if self.state.is_inverted() else False,
            arm_deg=getattr(self.entity, 'arm_deg', None),
            gun_name=getattr(self.entity, 'gun_held', None),
            hitbox=get_ent_rect(self.entity)
        )

        return where
        # return None

    def apply_vertical_push(self):
        # enemies will not jump, so this is only for player
        if not self.state.can_jump(self.entity.shape.body):
            return

        if self.state.get_state() != StateName.JUMP:
            self.state.change_state(StateName.JUMP, self.entity.get_position(), self.entity.shape.body,
                                    settings=self.entity.settings)

        force = Vec2d(
            0, -self.entity.settings["physics"]["ent_jump_force"]
        )
        self.entity.shape.body.apply_impulse_at_local_point(force)

    def apply_horizontal_velocity(self, direction: Direction):
        if self._should_run():
            self.state.change_state(StateName.RUN, self.entity.get_position(), self.entity.shape.body)

        if direction == Direction.LEFT:
            self.state.set_direction(Direction.LEFT, position=self.entity.get_position())
        else:
            self.state.set_direction(Direction.RIGHT, position=self.entity.get_position())

        self._calc_and_apply_velocity()

    def _should_run(self):
        return (
            self.state.get_state() != StateName.RUN and
            self.entity.shape.body.velocity.y == 0 and
            self.state.is_on_ground
        )

    def _calc_and_apply_velocity(self):
        velocity = Vec2d(
            self.movement if self.state.movement_direction == Direction.RIGHT else -self.movement,
            self.entity.shape.body.velocity.y
        )
        self.entity.shape.body.velocity = velocity

