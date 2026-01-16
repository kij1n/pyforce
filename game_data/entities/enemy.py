from .state_manager import StateManager
from .entity_helper import prepare_collision_box
from loguru import logger
from shared import *


class Enemy:
    def __init__(self, name: EnemyName, skin_color: SkinColor, settings: dict, pos, ent_id):
        self.name = name
        self.skin_color = skin_color  # flying or ground
        self.settings = settings

        self.body, self.shape, self.feet = prepare_collision_box(
            name.value, settings, pos, ent_id=ent_id
        )

        self.state_manager = StateManager(self)

        self.patrol_path = None
        self.aggro = False

        # action is not state
        self.current_action = None

    def __eq__(self, other):
        return self.get_id() == other.get_id()

    def __hash__(self):
        return hash(self.get_id())

    def get_id(self):
        return self.body.id

    def get_sprite_qty(self, state):
        return len(self.settings["enemy_info"][self.name.value]["sprites_paths"][state])

    def get_position(self):
        return self.shape.body.position

    def get_collision_box(self):
        return [self.body, self.shape, self.feet]

    def is_patrolling(self):
        return self.patrol_path is not None

    def get_movement_direction(self):
        return self.state_manager.state.movement_direction

    def get_current_action(self) -> EnemyAction:
        return self.current_action

    def update_patrol_state(self, patrol_paths):
        if self.patrol_path is None:
            path = self._is_on_patrol_path(patrol_paths)
            if path is not None:
                logger.debug("found patrol path")
                self._set_patrol_path(path)
                return True
            return False  # return false if a patrol path is not set
        if self._is_at_end_of_path():
            self._bounce_on_path()
        if not self._is_still_on_path():
            self.patrol_path.remove_enemy(self)
        return True

    def _is_still_on_path(self):
        return self.patrol_path.is_in(
            self.shape.body.position.x,
            self._get_y_range()
        )

    def _bounce_on_path(self):
        direction = self.get_movement_direction()
        direction = self._invert_direction(direction)
        self.state_manager.state.set_direction(
            direction,
            self.get_position()
        )

    @staticmethod
    def _invert_direction(direction):
        if direction == Direction.LEFT:
            return Direction.RIGHT
        return Direction.LEFT

    def _is_at_end_of_path(self):
        return self.patrol_path.is_at_end(
            self.shape.body.position.x,
            self.get_movement_direction()
        )

    def _set_patrol_path(self, path):
        if path is None:
            self.patrol_path.remove_enemy(self)
            self.change_action(EnemyAction.IDLE)
            return

        self.patrol_path = path
        path.add_enemy(self)
        self.change_action(EnemyAction.PATROL)

    def _is_on_patrol_path(self, patrol_paths):
        for path in patrol_paths:
            if path.is_in(
                self.shape.body.position.x,
                self._get_y_range()
            ):
                return path
        return None

    def _get_y_range(self):
        height = self._get_height()
        return (
            self.shape.body.position.y - height // 2,
            self.shape.body.position.y + height // 2
        )

    def _get_height(self):
        vertices = self.shape.get_vertices()
        return vertices[0].y * 2  # vertices are in local coordinates

    def change_action(self, action: EnemyAction):
        if self.current_action == action:
            return

        self.current_action = action
        if action in [EnemyAction.AGGRO, EnemyAction.PATROL]:
            self.state_manager.state.change_state("run", self.get_position(), self.body)

        self._log_action_change()

    def _log_action_change(self):
        if self.current_action == EnemyAction.AGGRO:
            logger.debug(f"Enemy {self.name.value} found player")
        elif self.current_action == EnemyAction.PATROL:
            logger.debug(f"Enemy {self.name.value} found patrol path")
        else:
            logger.debug(f"Enemy {self.name.value} lost player and patrol path, is now idle")

    def get_patrol_coords(self):
        x_range = (
            self.shape.body.position.x,
            self.shape.body.position.x + self.shape.width
        )
        return x_range, self.shape.body.position.y
