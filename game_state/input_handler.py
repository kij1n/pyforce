"""
This module contains the InputHandler class which manages user inputs.
"""
import pygame
from loguru import logger
from shared import GameState, Direction


class InputHandler:
    """
    The InputHandler class handles all user input, including keyboard, mouse, and pygame events.

    Attributes:
        controller (Controller): The main controller instance.
    """

    def __init__(self, controller):
        """
        Initializes the InputHandler with a reference to the controller.

        :param controller: The main controller instance.
        :return: None
        """
        self.controller = controller

    def handle(self):
        """
        Handles all types of input.

        :return: None
        """
        self.handle_events()
        self.handle_keys()

    def handle_events(self):
        """
        Handles pygame events like quitting the game.

        :return: None
        """
        if self.controller.game_state in [GameState.MENU, GameState.PAUSE]:
            return
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.controller.running = False

    def handle_keys(self):
        """
        Handles keyboard and mouse button presses for player movement and shooting.

        :return: None
        """
        keys = pygame.key.get_pressed()

        if keys[pygame.K_a]:
            self.controller.model.move_player(Direction.LEFT)
        if keys[pygame.K_d]:
            self.controller.model.move_player(Direction.RIGHT)
        if keys[pygame.K_w] or keys[pygame.K_SPACE]:
            self.controller.model.move_player(Direction.UP)
        if keys[pygame.K_ESCAPE]:
            self.controller.game_state = GameState.PAUSE

        keys = pygame.mouse.get_pressed()

        if keys[0]:  # Left mouse button
            self.controller.model.player_shoot()

    def handle_menu_clicks(self, ui):
        """
        Handles input related to menu interactions.

        :param ui: The GameUI instance to check for state changes.
        :return: None
        """
        if ui.change_game_state == GameState.PLAYING:
            self.controller.game_state = GameState.PLAYING
        elif ui.change_game_state == GameState.QUIT:
            self.controller.running = False
