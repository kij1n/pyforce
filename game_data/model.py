"""
This module contains the Model class which acts as the main data and logic coordinator for the game.
"""
from shared import Where, DebugElements, Difficulty, GameMode
from .physics import PhysicsEngine
from . import entities
from loguru import logger


class Model:
    """
    The Model class manages the game state, physics simulation, and entities.

    Attributes:
        settings (dict): Dictionary containing game settings.
        physics (PhysicsEngine): The physics engine managing the simulation.
        entities (EntityManager): Manages all game entities (player, enemies, bullets).
        where_array (list[Where]): Current rendering information for all entities.
        debug_elements (DebugElements): Information used for debug rendering.
    """

    def __init__(self, settings: dict, player_stats):
        """
        Initializes the Model with settings, physics engine, and entity manager.

        :param settings: Dictionary containing game settings.
        :return: None
        """
        logger.info("Initializing model...")

        self.settings = settings
        self.player_stats = player_stats

        self.physics = PhysicsEngine(self.settings)
        self.entities = entities.EntityManager(self.settings, self.physics.sim)
        self.insert_ents_to_sim()

        self.where_array = self._create_where()
        self.debug_elements = self._add_debug()

    def apply_difficulty(self, difficulty: Difficulty):
        self.entities.apply_difficulty(difficulty)

    def game_ended(self, game_mode: GameMode):
        """
        Checks if the game is still ongoing (player is alive).

        :return: True if the player exists, False otherwise.
        """
        if game_mode == GameMode.SPEEDRUN and len(self.entities.enemies) == 0:
            return True

        return self.entities.player is None

    def update(self, mouse_pos):
        """
        Updates the game state for a single frame.

        :param mouse_pos: The current position of the mouse.
        :return: None
        """
        self.entities.update_entity_states()
        self.entities.update_timers()
        self.entities.update_ground_contact(self.physics.entities_touching_ground)
        self.entities.update_enemy_action(self.physics.sim)
        self.entities.update_player_aim(mouse_pos)
        self.entities.update_bullets()

        self.where_array = self.entities.get_where_array()

        self.physics.sim.step(self.settings["physics"]["time_step"])
        self.entities.handle_hits(self.physics.entities_hit, self.physics.sim)
        self.entities.handle_kills(self.physics.entities_to_kill)

        if self.player_stats.game_mode == GameMode.INFINITE:
            self._spawn_enemy()

    def _spawn_enemy(self):
        max_enemies = self.settings["difficulty_changes"][self.player_stats.difficulty.value]["max_enemies_on_map"]
        if len(self.entities.enemies) < max_enemies:
            self.entities.spawn_random_enemy()

    def _add_debug(self):
        """
        Creates a DebugElements instance for visualization.

        :return: A DebugElements instance.
        """
        return DebugElements(self.physics.sim, self.entities.patrol_paths, self._add_bbs())

    def _add_bbs(self):
        """
        Collects bounding boxes for debug rendering.

        :return: A list of pygame.Rect objects.
        """
        bbs = []
        if self.settings["debug"]["show_bbs"]:

            for i in self.where_array:
                bbs.append(i.hitbox)
        return bbs

    def get_center_pos(self) -> tuple[int, int]:
        """
        Retrieves the center position for the camera, typically the player's position.

        :return: A tuple (x, y) representing the center position.
        """
        player_pos = self.entities.get_player_pos()
        return player_pos

    def get_where_array(self) -> list[Where]:
        """
        Returns the current list of rendering information for entities.

        :return: A list of Where objects.
        """
        return self.where_array

    def get_bullets_dict(self):
        """
        Returns the dictionary of active bullets and their shapes.

        :return: A dictionary mapping Bullet to pymunk.Shape.
        """
        return self.entities.bullets_dict

    def _create_where(self):
        """
        Generates the initial where_array.

        :return: A list of Where objects.
        """
        return self.entities.get_where_array()

    def insert_ents_to_sim(self):
        """
        Adds all initial entities to the physics simulation.

        :return: None
        """
        ents = self.entities.get_entities()
        for ent in ents:
            body, shape, feet = ent.get_collision_box()
            self.physics.sim.add(body, shape, feet)

    def move_player(self, direction: str):
        """
        Triggers player movement in a specified direction.

        :param direction: The direction to move (from Direction enum).
        :return: None
        """
        if self.entities.player.is_dying():
            return

        self.entities.move_player(direction)

    def player_shoot(self):
        """
        Triggers the player's shooting action and adds the bullet to the simulation.

        :return: None
        """
        if self.entities.player.is_dying():
            return

        body, shape, bullet = self.entities.get_bullet()

        if body is None or shape is None or bullet is None:
            return

        self.physics.sim.add(body, shape)
        self.entities.bullets_dict[bullet] = shape
