"""
This module contains the Controller class which is the main entry point for the game logic.
"""
import pygame

from game_view import View
from game_data import Model
from shared import GameState

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

        self.view = View(self.settings)
        self.model = Model(self.settings)

        self.fps = pygame.time.Clock()
        self.input_handler = InputHandler(self)
        self.game_state = GameState.MENU

        self.running = False

        self.game_mode = None
        self.difficulty = None

    def run(self):
        """
        Starts and manages the main game loop.

        :return: None
        """
        self.running = True

        while self.running and self.model.game_not_lost():
            self.view.render(
                self.model.get_center_pos(),
                self.model.get_where_array(),
                self.model.get_bullets_dict(),
                self.model.debug_elements,
                self.game_state,
            )

            if self.game_state == GameState.PLAYING:
                # only update the model if the game is running
                self.model.update(pygame.mouse.get_pos())

            if self.game_state in [GameState.MENU, GameState.PAUSE]:
                self.input_handler.handle_menu_clicks(self.view.ui)

            self.input_handler.handle()

            self.fps.tick(self.settings["fps"])

        pygame.quit()
