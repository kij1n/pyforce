"""
This module contains the StateManager class which acts as an interface between an entity and its state.
"""
from loguru import logger
from pymunk import Vec2d
from shared import *
from .state import *
from .entity_utils import get_ent_rect


class StateManager:
    """
    The StateManager class handles high-level state transitions and physical forces for an entity.

    Attributes:
        entity (Player|Enemy): The entity instance this manager belongs to.
        name (str): The name identifier of the entity.
        movement (float): Horizontal movement speed of the entity.
        state (State): The internal State instance tracking animation and physics.
    """

    def __init__(self, entity):
        """
        Initializes the StateManager for a given entity.

        :param entity: The entity instance.
        :return: None
        """
        self.entity = entity

        self.name = getattr(self.entity.name, "value", "player")
        if self.name == "player":
            self.movement = self.entity.settings["player_info"]["move_horizontal"]
        else:
            self.movement = self.entity.settings["enemy_info"][self.name]["move_horizontal"]

        self.state = State(StateName.IDLE, self.entity.get_position(), self)

    def get_where(self) -> Where:
        """
        Gathers all necessary information about the entity to create a Where dataclass for rendering.

        :return: A Where dataclass instance.
        """
        # if player_pos is None:
        where = Where(
            position=self.entity.get_position(),
            name=getattr(self.entity.name, "value", "player"),
            sprite_index=self.state.get_sprite_index(
                self.entity.get_position(),
                self.entity.get_sprite_qty(self.state.get_state_str()),
                self.entity.settings["sprites"]["cycle_lengths"][self.name].get(self.state.get_state_str(), None),
                self.entity.shape.body.velocity,
            ),
            state=self.state.get_state(),
            inversion=True if self.state.is_inverted() else False,
            arm_deg=getattr(self.entity, "arm_deg", None),
            gun_name=getattr(self.entity, "gun_held", None),
            hitbox=get_ent_rect(self.entity),
            is_dead=True if self.state.get_state() == StateName.DEATH else False,
            health_percent=self.entity.health / self.entity.max_health,
            guns_available=getattr(self.entity, "guns_available", None),
        )

        return where
        # return None

    def apply_vertical_push(self):
        """
        Applies an upward impulse to the entity's physics body if jumping is possible.

        :return: None
        """
        if not self.state.can_jump(self.entity.shape.body):
            return

        if self.state.get_state() != StateName.JUMP:
            # logger.debug(f"Jumping {self.entity.name}, state before change: {self.state.get_state()}")
            self.state.change_state(
                StateName.JUMP, self.entity.get_position(), self.entity.shape.body, settings=self.entity.settings
            )
            # logger.debug(f"Jumping {self.entity.name}, state after change: {self.state.get_state()}")

        force = Vec2d(0, -self.entity.settings["physics"]["ent_jump_force"])
        self.entity.shape.body.apply_impulse_at_local_point(force)

    def apply_horizontal_velocity(self, direction: Direction):
        """
        Applies horizontal velocity to the entity in the specified direction.

        :param direction: The Direction (LEFT or RIGHT) of movement.
        :return: None
        """
        if self._should_run():
            self.state.change_state(StateName.RUN, self.entity.get_position(), self.entity.shape.body)

        if direction == Direction.LEFT:
            self.state.set_direction(Direction.LEFT, position=self.entity.get_position())
        else:
            self.state.set_direction(Direction.RIGHT, position=self.entity.get_position())
        self._calc_and_apply_velocity()

    def _should_run(self):
        """
        Checks if the entity should transition to the RUN state.

        :return: True if the entity should run, False otherwise.
        """
        return (
            self.state.get_state() != StateName.RUN
            and self.entity.shape.body.velocity.y == 0
            and self.state.is_on_ground
            and getattr(self.entity, "current_action", None) != EnemyAction.ATTACK
        )

    def _calc_and_apply_velocity(self):
        """
        Calculates and sets the final velocity on the entity's physics body.

        :return: None
        """
        velocity = Vec2d(
            self.movement if self.state.movement_direction == Direction.RIGHT else -self.movement,
            self.entity.shape.body.velocity.y,
        )
        self.entity.shape.body.velocity = velocity
