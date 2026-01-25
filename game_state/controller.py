"""
This module contains the Controller class which is the main entry point for the game logic.
"""
import pygame

from game_view import View
from game_data import Model
from shared import GameState, PlayerStats, GameMode

from .input_handler import InputHandler
from .json_manager import JSONManager

from loguru import logger


class Controller:
    """
    The Controller class manages the main game loop and coordinates between the Model, View, and InputHandler.

    Attributes:
        json_manager (JSONManager): Manages loading and saving of settings.
        settings (dict): Dictionary containing game settings.
        view (View): Handles game rendering.
        model (Model): Manages game data and logic.
        fps (pygame.time.Clock): Controls the game's frame rate.
        input_handler (InputHandler): Processes user input.
        game_state (GameState): Current state of the game.
        running (bool): Flag to keep the game loop running.
    """

    def __init__(self):
        """
        Initializes the Controller with settings, view, model, and input handler.

        :return: None
        """
        logger.info("Initializing controller...")

        self.json_manager = JSONManager()
        self.settings = self.json_manager.settings
        self.player_stats = PlayerStats()

        self.view = View(self.settings)
        self.model = Model(self.settings, self.player_stats)

        self.fps = pygame.time.Clock()
        self.input_handler = InputHandler(self)
        self.game_state = GameState.MENU

        self.running = False

    def run(self):
        """
        Starts and manages the main game loop.

        :return: None
        """
        self.running = True

        while self.running and not self.model.game_ended(self.player_stats.game_mode):
            self._update_player_stats()

            self.view.render(
                self._prepare_render_info()
                # self.model.get_center_pos(),
                # self.model.get_where_array(),
                # self.model.get_bullets_dict(),
                # self.model.debug_elements,
                # self.game_state,
                # self.player_stats,
                # self.model.effects.get_effects(),
                # self.model.pickups.get_pickups()
            )

            if self.game_state == GameState.PLAYING:
                # only update the model if the game is running
                self.model.update(pygame.mouse.get_pos())

            if self.game_state in [GameState.MENU, GameState.PAUSE]:
                self.input_handler.handle_menu_clicks(self.view.ui)

            self.input_handler.handle()

            self.fps.tick(self.settings["fps"])

        if self._should_save_score():
            self._update_player_stats()
            self.json_manager.append_record(self.player_stats)
        pygame.quit()

    def _prepare_render_info(self):
        info = self.model.get_render_info()
        info.game_state = self.game_state
        info.player_stats = self.player_stats
        return info

    def _should_save_score(self):
        return (
            self.player_stats.game_mode == GameMode.INFINITE or
            (self.player_stats.game_mode == GameMode.SPEEDRUN and len(self.model.entities.enemies) == 0)
        )

    def _update_player_stats(self):
        self.player_stats.time_elapsed = pygame.time.get_ticks()
        self.player_stats.killed_enemies = self.model.entities.enemies_killed