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

            self.view.render(self._prepare_render_info())

            if self.game_state == GameState.PLAYING:
                # only update the model if the game is running
                self.model.update(pygame.mouse.get_pos())

            if self.game_state in [GameState.MENU, GameState.PAUSE]:
                self.input_handler.handle_menu_clicks(self.view.ui)

            self.input_handler.handle()

            self.fps.tick(self.settings["fps"])

        return self._should_restart()

    def _should_restart(self):
        """
        Determines if the game should restart based on user input after the game ends.
        Also handles saving the player's score if applicable.

        :return: True if the game should restart, False otherwise.
        """
        if self.game_state == GameState.QUIT:
            return False

        if self._can_save_score():
            self._save_score()

        self.view.ui.start_restart_mainloop()
        return self.view.ui.restart

    def _save_score(self):
        """
        Helper method to ask whether to save and save the player's score if applicable.
        :return:
        """
        self.view.ui.start_save_mainloop()
        if self.view.ui.save_score:
            self._update_player_stats()
            self.json_manager.append_record(self.player_stats)

    def _prepare_render_info(self):
        """
        Collects and prepares all necessary information for rendering the current game state.

        :return: A RenderInfo instance containing data for the view.
        """
        info = self.model.get_render_info()
        info.game_state = self.game_state
        info.player_stats = self.player_stats
        return info

    def _can_save_score(self):
        """
        Checks if the current game conditions allow for saving the player's score.

        :return: True if the score can be saved, False otherwise.
        """
        return self.player_stats.game_mode == GameMode.INFINITE or (
            self.player_stats.game_mode == GameMode.SPEEDRUN and len(self.model.entities.enemies) == 0
        )

    def _update_player_stats(self):
        """
        Updates the player's statistics with the latest game data.

        :return: None
        """
        self.player_stats.time_elapsed = pygame.time.get_ticks()
        self.player_stats.killed_enemies = self.model.entities.enemies_killed
