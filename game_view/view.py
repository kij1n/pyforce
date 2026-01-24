"""
This module contains the View class which handles the overall rendering of the game.
"""
from shared import GameState, PlayerStats
from .ui import GameUI
from .entity_renderer import *
from .sprite_loader import *
from .map_renderer import MapRenderer

from loguru import logger

import pymunk
import pymunk.pygame_util


class View:
    """
    The View class is responsible for managing the game's window and rendering all game elements.

    Attributes:
        settings (dict): Dictionary containing game settings.
        size (tuple): The width and height of the game window.
        screen (pygame.Surface): The main display surface.
        ui (GameUI): Handles user interface elements like menus.
        sprite_loader (SpriteLoader): Manages loading and caching of sprites.
        entity_renderer (EntityRenderer): Handles rendering of game entities.
        map_renderer (MapRenderer): Handles rendering of the game map.
    """

    def __init__(self, settings: dict):
        """
        Initializes the View with the given settings.

        :param settings: Dictionary containing game settings.
        :return: None
        """
        logger.info("Initializing view...")

        self.settings = settings
        self.size = (settings["screen"]["size_x"], settings["screen"]["size_y"])

        pygame.display.set_caption(self.settings["title"])
        self.screen = pygame.display.set_mode(self.size)

        pygame.init()

        self.ui = GameUI(self.settings, self.screen)
        self.sprite_loader = SpriteLoader(self.settings)
        self.entity_renderer = EntityRenderer()
        self.map_renderer = MapRenderer(self.size, self.settings)

    def render(self, player_pos, where_array: list[Where], bullets_set, debug_elements, game_state: GameState, player_stats: PlayerStats):
        """
        Renders the entire game scene based on the current game state.

        :param player_stats: PlayerStats object containing player stats.
        :param player_pos: The current position of the player.
        :param where_array: A list of Where objects containing information about where to render entities.
        :param bullets_set: A set of active bullets to render.
        :param debug_elements: An object containing debug information to render.
        :param game_state: The current state of the game, a GameState enum value.
        :return: None
        """
        if game_state == GameState.MENU:
            self.ui.change_game_state = game_state
            self.ui.render(self.sprite_loader, events=pygame.event.get())
            pygame.display.flip()
            return
        if game_state == GameState.PAUSE:
            self.ui.change_game_state = game_state
            self.ui.render_pause(self.sprite_loader, events=pygame.event.get())
            pygame.display.flip()
            return

        self.map_renderer.render(player_pos, self.screen, self.sprite_loader)
        self.entity_renderer.render(where_array, self.sprite_loader, self.screen, self.settings, player_pos)
        self.entity_renderer.render_bullets(bullets_set, self.sprite_loader, self.screen, self.settings, player_pos)
        self.ui.render_player_stats(player_stats)

        # DEBUG DRAWING
        self._render_debug_info(player_pos, debug_elements)
        # DEBUG DRAWING

        pygame.display.flip()

    def _render_debug_info(self, player_pos, debug_elements):
        """
        Renders debug information such as hitboxes and patrol paths.

        :param player_pos: The current position of the player.
        :param debug_elements: An object containing debug information to render.
        :return: None
        """
        abs_camera_pos, rel_camera_pos = calc_camera_pos(self.settings, player_pos)
        vector = (rel_camera_pos[0] - abs_camera_pos[0], rel_camera_pos[1] - abs_camera_pos[1])

        if self.settings["debug"]["show_hitboxes"]:
            self._render_hitboxes(debug_elements.sim, vector)

        if self.settings["debug"]["show_patrol_paths"]:
            self._render_patrol_paths(debug_elements.patrol_paths, vector)

        if self.settings["debug"]["show_fps"]:
            pass

        if self.settings["debug"]["show_bbs"]:
            self._render_bbs(debug_elements.bbs)

    def _render_bbs(self, bbs):
        """
        Renders bounding boxes for debugging.

        :param bbs: A list of pygame.Rect objects representing bounding boxes.
        :return: None
        """
        if bbs is None:
            return
        for rect in bbs:
            # we don't need to translate the rect, because it's already in relative coordinates
            pygame.draw.rect(self.screen, "red", rect)

    def _render_hitboxes(self, sim: pymunk.Space, vector: tuple[int, int]):
        """
        Renders hitboxes from the physics simulation for debugging.

        :param sim: The pymunk Space object containing the physics simulation.
        :param vector: The translation vector for the camera.
        :return: None
        """
        draw_options = pymunk.pygame_util.DrawOptions(self.screen)
        draw_options.transform = pymunk.Transform.translation(vector[0], vector[1])
        sim.debug_draw(draw_options)

    def _render_patrol_paths(self, patrol_paths, vector):
        """
        Renders patrol paths for enemies for debugging.

        :param patrol_paths: A list of patrol path objects.
        :param vector: The translation vector for the camera.
        :return: None
        """
        for path in patrol_paths:
            x1 = path.start[0]
            x2 = path.end[0]
            y = path.start[1]

            rect = pygame.Rect((x1 + vector[0], y + vector[1]), (x2 - x1, 10))

            pygame.draw.rect(self.screen, (255, 0, 0), rect)
