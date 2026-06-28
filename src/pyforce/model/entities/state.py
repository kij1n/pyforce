"""
This module contains the State class which manages the internal state and animation logic of an entity.
"""

import weakref

from loguru import logger
from pymunk import Vec2d
from shared import StateName, Direction, EnemyAction, EnemyName


class State:
    """
    The State class tracks and calculates values related to an entity's current animation and physical state.

    Attributes:
        state_manager (StateManager): Reference to the state manager.
        settings (dict): Dictionary containing game settings.
        state (StateName): The current animation/behavioral state.
        start_pos (Vec2d): The position where the current state started.
        dead (bool): Flag indicating if the death process (including wait time) is complete.
        previous_hits (int): Number of hits performed by the entity in the previous frame.
        hits (int): Cumulative number of hits performed in the current state.
        start_time (int): The timestamp (in ticks) when the state started.
        current_time (int): The current relative timestamp (in ticks) within the state.
        death_time (int): The duration of the death animation.
        wait_after_death (int): Total time to wait after death before removal.
        attack_time (int): The duration of the attack animation cycle.
        start_y (float): The Y coordinate where a jump started.
        highest_y (float): The calculated peak Y coordinate of a jump.
        achieved_highest_y (bool): Whether the entity has reached the peak of its jump.
        movement_direction (Direction): The current horizontal movement direction.
        is_on_ground (bool): Whether the entity is currently touching the ground.
    """

    def __init__(self, state, position: Vec2d, state_manager):
        """
        Initializes the State with an initial state name and position.

        :param state: The initial StateName.
        :param position: The starting Vec2d position.
        :param state_manager: The StateManager instance.
        :return: None
        """
        self.state_manager = weakref.proxy(state_manager)
        self.settings = state_manager.entity.settings

        self.state = state
        self.start_pos = position
        self.dead = False

        self.dealt_damage = False
        self.has_hit = False
        self.previous_hits = 0
        self.hits = 0
        self.start_time = 0
        self.current_time = 0
        self.death_time = self.settings["sprites"]["cycle_lengths"][self.state_manager.name]["death_time"]
        self.wait_after_death = self.settings["sprites"]["cycle_lengths"][self.state_manager.name]["wait_after_death"]
        self.dead = False
        self.attack_time = self.settings["sprites"]["cycle_lengths"][self.state_manager.name]["attack_time"]

        self.start_y = None
        self.highest_y = None
        self.achieved_highest_y = False

        self.movement_direction = None
        self.is_on_ground = False

    def is_inverted(self):
        """
        Determines if the sprite should be horizontally flipped based on movement direction.

        :return: True if moving left, False otherwise.
        """
        return True if self.movement_direction == Direction.LEFT else False

    def can_jump(self, body) -> bool:
        """
        Checks if the entity is in a physical state that allows jumping.

        :param body: The pymunk Body of the entity.
        :return: True if jumping is possible, False otherwise.
        """
        return self.is_on_ground and body.velocity.y >= 0

    def set_on_ground(self, is_on_ground: bool):
        """
        Updates the ground contact status.

        :param is_on_ground: Boolean value.
        :return: None
        """
        self.is_on_ground = is_on_ground

    def get_sprite_index(
        self, current_position: Vec2d, total_sprites: int, cycle_length: float, velocity: Vec2d
    ) -> int:
        """
        Calculates the current sprite frame index based on state, position, and time.

        :param current_position: The entity's current position.
        :param total_sprites: Total number of sprites specified in the settings.
        :param cycle_length: Duration (or distance) for one frame.
        :param velocity: The entity's current velocity.
        :return: The frame index.
        """
        if total_sprites <= 1:
            logger.error("Invalid total sprites")
            return 0

        if self.state == StateName.RUN:
            return self._handle_run(current_position, total_sprites, cycle_length)
        elif self.state == StateName.IDLE:
            return self._handle_idle(cycle_length, total_sprites)
        elif self.state == StateName.JUMP:
            return self._handle_jump(current_position, total_sprites, velocity)
        elif self.state == StateName.DEATH:
            return self._handle_death(total_sprites)
        elif self.state == StateName.ATTACK:
            return self._handle_attack(total_sprites)

        return 0

    def _handle_attack(self, total_sprites):
        """
        Calculates sprite index for the ATTACK state.

        :param total_sprites: Total number of sprites.
        :return: Sprite index.
        """
        if self.current_time >= self.attack_time:
            self.current_time = 0

            if self.state_manager.entity.name == EnemyName.GOBLIN:
                self.hits += 1
                self.has_hit = True
            else:
                self.has_hit = False
                self.dealt_damage = False

            return total_sprites - 1

        step = self.attack_time / total_sprites
        if self._check_skeleton_hit(total_sprites, step):
            self.has_hit = True
            self.hits += 1
            self.dealt_damage = True

        return int(self.current_time // step)

    def _check_skeleton_hit(self, total_sprites, step):
        """
        Skeletons need to deal damage when they reach half the sprites
        during animation.
        :param total_sprites: Total number of sprites
        :param step: Time per sprite
        :return: Boolean whether a skeleton has hit
        """
        return (
            int(self.current_time // step) >= total_sprites // 2
            and not self.has_hit
            and self.state_manager.entity.name == EnemyName.SKELETON
            and not self.dealt_damage
        )

    def _handle_death(self, total_sprites):
        """
        Calculates sprite index for the DEATH state and updates the dead flag.

        :param total_sprites: Total number of sprites.
        :return: Sprite index.
        """
        if self.current_time >= self.wait_after_death:
            self.dead = True
        if self.current_time >= self.death_time:
            return total_sprites - 1

        step = self.death_time / total_sprites
        return int(self.current_time // step)

    def _handle_run(self, current_position, total_sprites, cycle_length):
        """
        Calculates sprite index for the RUN state based on distance moved.

        :param current_position: Current position.
        :param total_sprites: Total number of sprites.
        :param cycle_length: Distance traveled per sprite.
        :return: Sprite index.
        """
        current_x = current_position.x
        start_x = self.start_pos.x

        distance_moved = abs(current_x - start_x)
        full_cycle = cycle_length * total_sprites
        rest_of_dist = distance_moved % full_cycle

        return int(rest_of_dist // cycle_length)

    def _handle_idle(self, cycle_length, total_sprites):
        """
        Calculates sprite index for the IDLE state based on elapsed time.

        :param cycle_length: Duration per sprite.
        :param total_sprites: Total number of sprites.
        :return: Sprite index.
        """
        time_elapsed = self.current_time - self.start_time
        full_cycle = cycle_length * total_sprites
        rest_of_time = time_elapsed % full_cycle

        return int(rest_of_time // cycle_length)

    def _handle_jump(self, current_position, total_sprites, velocity):
        """
        Calculates sprite index for the JUMP state based on vertical height relative to peak.

        :param current_position: Current position.
        :param total_sprites: Total number of sprites.
        :param velocity: Current velocity.
        :return: Sprite index.
        """
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
        """
        Inverts a frame index for the downward portion of a jump animation.

        :param index: The sprite index.
        :param total_sprites: Total sprites.
        :return: The reversed sprite index.
        """
        return total_sprites - 1 - index

    def append_time(self):
        """
        Increments the state's relative timer for time-based animations.

        :return: None
        """
        if self.state in [StateName.IDLE, StateName.DEATH, StateName.ATTACK]:
            self.current_time += 1

    def set_direction(self, direction, position=None):
        """
        Updates the horizontal movement direction.

        :param direction: The new Direction.
        :param position: Optional position to reset the start position for distance-based animations.
        :return: None
        """
        if direction != self.movement_direction:
            self.movement_direction = direction
            self.start_pos = position

    def change_state(self, new_state: EnemyAction, position: Vec2d, body, settings=None):
        """
        Transitions the internal state to a new StateName and resets relevant timers and counters.

        :param new_state: The new state name.
        :param position: Current position.
        :param body: The physics body.
        :param settings: Optional game settings (required for JUMP state).
        :return: None
        """
        self.state = new_state

        if new_state == StateName.RUN:
            self.start_pos = position

        elif new_state in [StateName.IDLE, StateName.DEATH, StateName.ATTACK]:
            self.start_time = 0
            self.current_time = 0
            self.hits = 0
            self.previous_hits = 0

        elif new_state == StateName.JUMP:
            if self.state_manager.name != "player":
                self.start_pos = position
            self.achieved_highest_y = False
            self.start_y = position.y
            self.highest_y = self._calc_highest_y(position.y, settings)

        body.activate()

    @staticmethod
    def _calc_highest_y(current_y, settings):
        """
        Calculates the peak Y-coordinate of a jump using physics parameters.

        :param current_y: Starting Y position.
        :param settings: Dictionary containing game settings.
        :return: The peak Y position.
        """
        J = settings["physics"]["ent_jump_force"]
        g = settings["physics"]["gravity"]
        m = settings["player_info"]["mass"]
        y_0 = current_y
        highest_y = abs(J**2 / (2 * g * m**2) - y_0)
        return highest_y

    def get_state(self) -> StateName:
        """
        Retrieves the current StateName enum.

        :return: The current StateName.
        """
        return self.state

    def get_ent_sp_settings(self):
        """
        Retrieves sprite path settings for the entity.

        :return: A dictionary of sprite paths.
        """
        if self.state_manager.name == "player":
            return self.settings["player_info"]["sprites_paths"]
        else:
            return self.settings["enemy_info"][self.state_manager.name]["sprites_paths"]

    def get_state_str(self) -> str:
        """
        Retrieves the string value of the current state.

        :return: State name as a string.
        """
        return self.state.value
