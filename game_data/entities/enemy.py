"""
This module contains the Enemy class, which represents an enemy entity in the game.
"""
from .state_manager import StateManager
from .entity_utils import prepare_collision_box
from loguru import logger
from shared import *


class Enemy:
    """
    The Enemy class manages the state, physics, and behavior of an enemy.

    Attributes:
        name (EnemyName): The name/type of the enemy.
        settings (dict): Dictionary containing game settings.
        health (int): Current health of the enemy.
        max_health (int): Maximum health of the enemy.
        damage_dealt (int): Damage the enemy deals to the player.
        entity_manager (EntityManager): Reference to the entity manager.
        body (pymunk.Body): Physics body of the enemy.
        shape (pymunk.Poly): Physics shape of the enemy.
        feet (pymunk.Shape): Physics shape for the enemy's feet (collision detection with ground).
        state_manager (StateManager): Manages the animation and movement state of the enemy.
        patrol_path (PatrolPath): The current patrol path the enemy is on, if any.
        aggro (bool): Whether the enemy is currently aggressive towards the player.
        current_action (EnemyAction): The current high-level action of the enemy.
    """

    def __init__(self, name: EnemyName, settings: dict, pos, ent_id, entity_manager):
        """
        Initializes an Enemy instance with its properties and physics components.

        :param name: The name/type of the enemy.
        :param settings: Dictionary containing game settings.
        :param pos: Initial position of the enemy.
        :param ent_id: Unique identifier for the entity.
        :param entity_manager: The EntityManager instance.
        :return: None
        """
        self.name = name
        self.settings = settings
        self.health = self.settings["enemy_info"][name.value]["health"]
        self.max_health = self.health
        self.damage_dealt = self.settings["enemy_info"][name.value]["damage"]
        self.entity_manager = entity_manager

        self.body, self.shape, self.feet = prepare_collision_box(name.value, settings, self, pos=pos, ent_id=ent_id)
        self.ent_id = ent_id

        self.state_manager = StateManager(self)

        self.patrol_path = None
        self.aggro = False

        # action is not state
        self.current_action = None

    def __eq__(self, other):
        """
        Checks equality between two Enemy instances based on their unique ID.

        :param other: The other object to compare.
        :return: True if IDs match, False otherwise.
        """
        return self.get_id() == other.get_id()

    def __hash__(self):
        """
        Returns the hash of the enemy based on its unique ID.

        :return: Hash value.
        """
        return hash(self.get_id())

    def __del__(self):
        """
        Destructor, for the Enemy instance, cleans up patrol path reference.

        :return: None
        """
        logger.info(f"{self.name.value} killed")
        if self.patrol_path is not None:
            self.patrol_path.remove_enemy(self)

    def has_hit(self):
        """
        Checks if the enemy has performed a hit during its current state.

        :return: True if a new hit has occurred, False otherwise.
        """
        state = self.state_manager.state
        if state.has_hit and state.previous_hits < state.hits:
            state.previous_hits = state.hits
            state.has_hit = False
            return True
        return False

    def get_state(self):
        """
        Retrieves the current animation state of the enemy.

        :return: The current state as a string or enum member.
        """
        return self.state_manager.state.get_state()

    def change_state(self, state):
        """
        Changes the enemy's animation state.

        :param state: The new state to transition to.
        :return: None
        """
        self.state_manager.state.change_state(state, self.get_position(), self.body)

    def get_id(self):
        """
        Retrieves the unique identifier of the enemy from its physics body.

        :return: The entity's ID.
        """
        return self.body.id

    def get_sprite_qty(self, state):
        """
        Returns the number of sprites available for a given state.

        :param state: The animation state.
        :return: The number of sprites.
        """
        # some enemies don't have jump sprites, they will use run instead
        return len(
            self.settings["enemy_info"][self.name.value]["sprites_paths"].get(
                state, self.settings["enemy_info"][self.name.value]["sprites_paths"][StateName.RUN.value]
            )
        )

    def get_position(self):
        """
        Retrieves the current world position of the enemy.

        :return: A tuple or Vec2d representing the position.
        """
        return self.shape.body.position

    def get_collision_box(self):
        """
        Retrieves the physics components of the enemy.

        :return: A list containing [body, shape, feet].
        """
        return [self.body, self.shape, self.feet]

    def is_patrolling(self):
        """
        Checks if the enemy is currently assigned to a patrol path.

        :return: True if patrolling, False otherwise.
        """
        return self.patrol_path is not None

    def get_movement_direction(self):
        """
        Retrieves the current movement direction of the enemy.

        :return: The current Direction.
        """
        return self.state_manager.state.movement_direction

    def get_current_action(self) -> EnemyAction:
        """
        Retrieves the current high-level action of the enemy.

        :return: The current EnemyAction.
        """
        return self.current_action

    def update_patrol_state(self, patrol_paths) -> bool:
        """
        Updates the enemy's patrol state, including path finding and bouncing at ends.

        :param patrol_paths: A list of available patrol paths.
        :return: True if the enemy is on a patrol path, False otherwise.
        """
        if self.patrol_path is not None and not self._is_still_on_path():
            self.patrol_path.remove_enemy(self)
            self.patrol_path = None
        if self.patrol_path is None:
            path = self._is_on_patrol_path(patrol_paths)
            if path is not None:
                self._set_patrol_path(path)
                return True
            return False  # return false if a patrol path is not set
        if self._should_bounce():
            self._bounce_on_path()
        return True

    def _is_still_on_path(self):
        """
        Checks if the enemy is still within its assigned patrol path.

        :return: True if on path, False otherwise.
        """
        return self.patrol_path.is_in(self.shape.body.position.x, self._get_y_range())

    def _bounce_on_path(self):
        """
        Inverts the enemy's movement direction when it reaches the end of its patrol path.

        :return: None
        """
        direction = self.get_movement_direction()
        direction = self._invert_direction(direction)
        self.state_manager.state.set_direction(direction, self.get_position())

    @staticmethod
    def _invert_direction(direction):
        """
        Inverts a given direction.

        :param direction: The direction to invert.
        :return: The inverted Direction.
        """
        if direction == Direction.LEFT:
            return Direction.RIGHT
        return Direction.LEFT

    def _should_bounce(self):
        """
        Checks if the enemy has reached the end of its patrol path in its current direction
        or collides with an enemy on the same path.

        :return: True if an entity should bounce, False otherwise.
        """
        return (
            self.patrol_path.is_at_end(self.shape.body.position.x, self.get_movement_direction()) or
            self.patrol_path.collides_with_another(self)
        )

    def _set_patrol_path(self, path):
        """
        Assigns a patrol path to the enemy.

        :param path: The PatrolPath instance to assign.
        :return: None
        """
        if path is None:
            self.patrol_path.remove_enemy(self)
            self.change_action(EnemyAction.IDLE)
            return

        self.patrol_path = path
        path.add_enemy(self)
        self.change_action(EnemyAction.PATROL)

    def _is_on_patrol_path(self, patrol_paths):
        """
        Identifies if the enemy's current position coincides with any given patrol path.

        :param patrol_paths: A list of PatrolPath instances.
        :return: The PatrolPath if found, None otherwise.
        """
        for path in patrol_paths:
            if path.is_in(self.shape.body.position.x, self._get_y_range()):
                return path
        return None

    def _get_y_range(self):
        """
        Calculates the Y-coordinate range of the enemy for path detection.

        :return: A tuple (min_y, max_y).
        """
        height = self._get_height()
        return self.shape.body.position.y - height // 2, self.shape.body.position.y + height // 2

    def _get_height(self):
        """
        Calculates the height of the enemy's physics shape.

        :return: The height value.
        """
        vertices = self.shape.get_vertices()
        return vertices[0].y * 2  # vertices are in local coordinates

    def change_action(self, action: EnemyAction):
        """
        Changes the enemy's current high-level action and corresponding animation state.

        :param action: The new EnemyAction to perform.
        :return: None
        """
        if self.current_action == action:
            return

        self.current_action = action
        if action in [EnemyAction.AGGRO, EnemyAction.PATROL]:
            self.state_manager.state.change_state(StateName.RUN, self.get_position(), self.body)
        elif action == EnemyAction.ATTACK:
            self.state_manager.state.change_state(StateName.ATTACK, self.get_position(), self.body)

        self._log_action_change()

    def _log_action_change(self):
        """
        Logs the change in the enemy's action for debugging purposes.

        :return: None
        """
        if self.current_action == EnemyAction.AGGRO:
            logger.debug(f"Enemy {self.name.value} found player")
        elif self.current_action == EnemyAction.PATROL:
            logger.debug(f"Enemy {self.name.value} found patrol path: {self.patrol_path.id}")
        elif self.current_action == EnemyAction.DEATH:
            logger.debug(f"Enemy {self.name.value} lost all hp")
        elif self.current_action == EnemyAction.ATTACK:
            logger.debug(f"Enemy {self.name.value} is attacking player")
        else:
            logger.debug(f"Enemy {self.name.value} lost player and patrol path, is now idle")

    def get_patrol_coords(self):
        """
        Retrieves coordinates used for patrol path calculations.

        :return: A tuple containing (x_range, y_position).
        """
        x_range = (self.shape.body.position.x, self.shape.body.position.x + self.shape.width)
        return x_range, self.shape.body.position.y

    def take_damage(self, damage):
        """
        Reduces the enemy's health by the specified damage amount.

        :param damage: The amount of damage to take.
        :return: None
        """
        if self.get_current_action() == EnemyAction.DEATH:
            return

        self.health -= damage

    def kill(self):
        """
        Removes the enemy from the game world.

        :return: None
        """
        self.entity_manager.remove_entity(self)

    def is_over_dying(self):
        """
        Checks if the enemy's death animation is completed.

        :return: True if dead, False otherwise.
        """
        return self.state_manager.state.dead
