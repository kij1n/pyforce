"""
This module contains the Player class which represents the player entity.
"""

import weakref

from loguru import logger

from shared import StateName
from .state_manager import StateManager
from .entity_utils import prepare_collision_box
from pymunk import Vec2d


class Player:
    """
    The Player class manages the player's state, movement, health, and equipment.

    Attributes:
        name (str): The name identifier for the player ("player").
        settings (dict): Dictionary containing game settings.
        entity_manager (EntityManager): Reference to the entity manager.
        health (int): Current health of the player.
        max_health (int): Maximum health of the player.
        body (pymunk.Body): Physics body of the player.
        shape (pymunk.Poly): Physics shape of the player.
        feet (pymunk.Shape): Physics shape for the player's feet (collision detection).
        state_manager (StateManager): Manages the player's animation and movement state.
        arm_deg (float): The current rotation angle of the player's arm.
        gun_held (str): The name of the currently held gun.
        ammo_used (str): The type of ammo currently used.
    """

    def __init__(self, settings: dict, entity_manager):
        """
        Initializes the Player instance with settings and a reference to the entity manager.

        :param settings: Dictionary containing game settings.
        :param entity_manager: The EntityManager instance.
        :return: None
        """
        self.name = "player"
        self.settings = settings
        self.entity_manager = weakref.proxy(entity_manager)
        self.health = self.settings["player_info"]["health"]
        self.max_health = self.health

        self.body, self.shape, self.feet = prepare_collision_box(self.name, settings, self)
        self.state_manager = StateManager(self)

        self.arm_deg = 0  # 0 means pointing down, turns counter-clockwise
        self.gun_held = "base"
        self.ammo_used = "base"
        self.guns_available = ["base"]

    def get_relative_pos(self):
        """
        Calculates the player's position relative to the screen, accounting for camera clamping.

        :return: A tuple (x, y) representing screen-relative coordinates.
        """
        player_abs_pos = self.get_position()

        screen_w = self.settings["screen"]["size_x"]
        screen_h = self.settings["screen"]["size_y"]
        map_w = self.settings["map"]["size_x"]
        map_h = self.settings["map"]["size_y"]

        # Calculate where the camera wants to be (centered on player)
        # Camera Top-Left = Player Center - Half Screen
        cam_x = player_abs_pos[0] - (screen_w // 2)
        cam_y = player_abs_pos[1] - (screen_h // 2)

        # Clamp the camera so it doesn't show outside the map
        cam_x = self._clamp(0, cam_x, map_w - screen_w)
        cam_y = self._clamp(0, cam_y, map_h - screen_h)

        # Relative Position = Absolute Position - Camera Position
        return player_abs_pos[0] - cam_x, player_abs_pos[1] - cam_y

    @staticmethod
    def _clamp(min_value, value, max_value):
        return max(min_value, min(value, max_value))

    def get_sprite_qty(self, state):
        """
        Retrieves the number of sprites available for a given animation state.

        :param state: The animation state.
        :return: The number of sprites.
        """
        return len(self.settings["player_info"]["sprites_paths"][state])

    def get_collision_box(self):
        """
        Retrieves the player's physics components.

        :return: A list containing [body, shape, feet].
        """
        return [self.body, self.shape, self.feet]

    def get_position(self) -> Vec2d:
        """
        Retrieves the player's current world position.

        :return: A Vec2d representing the absolute world position.
        """
        return self.shape.body.position

    def get_state(self):
        """
        Retrieves the player's current animation state.

        :return: The current state name.
        """
        return self.state_manager.state.get_state()

    def get_gun_position(self):
        """
        Retrieves the world position from which bullets are
        fired (currently player's center).

        :return: A Vec2d representing the firing position.
        """
        return self.shape.body.position

    def take_damage(self, damage):
        """
        Reduces the player's health by the specified damage amount.

        :param damage: The amount of damage to take.
        :return: None
        """
        self.health -= damage
        logger.debug(f"Player took {damage} damage, health: {self.health}")

    def change_state(self, state):
        """
        Changes the player's animation state.

        :param state: The new state to transition to.
        :return: None
        """
        self.state_manager.state.change_state(state, self.get_position(), self.body)

    def is_over_dying(self):
        """
        Checks if the player's death animation has finished.

        :return: True if a death process is complete, False otherwise.
        """
        return self.state_manager.state.dead

    def is_dying(self):
        """
        Checks if the player is currently in the death state.

        :return: True if dying, False otherwise.
        """
        return self.state_manager.state.state == StateName.DEATH

    def kill(self):
        """
        Removes the player from the game.

        :return: None
        """
        self.entity_manager.remove_entity(self)
