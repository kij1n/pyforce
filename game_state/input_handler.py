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
        self.mouse_map = {
            "mouse_left": 0,
            "mouse_middle": 1,
            "mouse_right": 2
        }

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
        mouse = pygame.mouse.get_pressed()
        key_bindings = self.controller.settings["key_bindings"]

        if self._check_binds(keys, mouse, key_bindings["move_left"]):
            self.controller.model.move_player(
                Direction.LEFT
            )
        if self._check_binds(keys, mouse, key_bindings["move_right"]):
            self.controller.model.move_player(
                Direction.RIGHT
            )
        if self._check_binds(keys, mouse, key_bindings["jump"]):
            self.controller.model.move_player(
                Direction.UP
            )
        if self._check_binds(keys, mouse, key_bindings["pause"]):
            self.controller.game_state = GameState.PAUSE
        if self._check_binds(keys, mouse, key_bindings["shoot"]):
            self.controller.model.player_shoot()

    def _check_binds(self, keys, mouse, binds: list):
        for key in binds:
            if key.startswith("mouse_"):
                num = self.mouse_map[key]
                if mouse[num]:
                    return True
            else:
                if keys[pygame.key.key_code(key)]:
                    return True
        return False

    def handle_menu_clicks(self, ui):
        """
        Handles input related to menu interactions.

        :param ui: The GameUI instance to check for state changes.
        :return: None
        """
        if ui.change_game_state == GameState.PLAYING:
            self.controller.game_state = GameState.PLAYING
            self.controller.game_mode = ui.selected_gamemode
            ui.change_game_state = None
        elif ui.change_game_state == GameState.QUIT:
            self.controller.running = False
            ui.change_game_state = None
