"""
This module contains the GameUI class which handles the user interface and menus.
"""
import pygame_menu
import pygame

from shared import GameState


class GameUI:
    """
    The GameUI class manages the game's menus using pygame_menu.

    Attributes:
        change_game_state (GameState): Stores the state the game should transition to.
        settings (dict): Dictionary containing game settings.
        theme (pygame_menu.Theme): The theme used for menus.
        menu (pygame_menu.Menu): The main menu.
        pause_menu (pygame_menu.Menu): The pause menu.
    """

    def __init__(self, settings: dict):
        """
        Initializes the GameUI with settings and creates menus.

        :param settings: Dictionary containing game settings.
        :return: None
        """
        self.change_game_state = None
        self.settings = settings
        self.theme = self._create_theme()

        self.menu = self._create_menu()
        self._add_menu_buttons()

        self.pause_menu = self._create_pause_menu()
        self._add_pause_buttons()

    def render_pause(self, screen, events):
        """
        Renders the pause menu.

        :param screen: The pygame Surface to render onto.
        :param events: A list of pygame events to process.
        :return: None
        """
        screen.fill(self.settings["theme_info"]["background_color"])
        self.pause_menu.update(events)
        self.pause_menu.draw(screen)

    def render(self, screen, events):
        """
        Renders the main menu.

        :param screen: The pygame Surface to render onto.
        :param events: A list of pygame events to process.
        :return: None
        """
        screen.fill(self.settings["theme_info"]["background_color"])
        self.menu.update(events)
        self.menu.draw(screen)

    def _create_pause_menu(self):
        """
        Creates the pause menu instance.

        :return: A pygame_menu.Menu instance.
        """
        menu = pygame_menu.Menu(
            self.settings["theme_info"]["pause_title"],
            width=self.settings["theme_info"]["menu_width"],
            height=self.settings["theme_info"]["menu_height"],
            theme=self.theme,
        )
        return menu

    def _add_pause_buttons(self):
        """
        Adds buttons to the pause menu.

        :return: None
        """
        self.pause_menu.add.button("Resume", self._play_game)
        self.pause_menu.add.button("Quit", self._stop_game)

    def _add_menu_buttons(self):
        """
        Adds buttons to the main menu.

        :return: None
        """
        self.menu.add.button("Play", self._play_game)
        self.menu.add.button("Quit", self._stop_game)

    def _create_theme(self):
        """
        Creates the theme for the menus.

        :return: A pygame_menu.Theme instance.
        """
        theme = pygame_menu.Theme(
            background_color=self.settings["theme_info"]["menu_background_color"],
            title_font=pygame_menu.font.FONT_MUNRO,
            title_font_shadow=self.settings["theme_info"]["font_shadow"],
            widget_padding=self.settings["theme_info"]["widget_padding"],
            widget_font=pygame_menu.font.FONT_MUNRO,
            widget_font_color=self.settings["theme_info"]["font_color"],
        )
        return theme

    def _create_menu(self):
        """
        Creates the main menu instance.

        :return: A pygame_menu.Menu instance.
        """
        menu = pygame_menu.Menu(
            self.settings["theme_info"]["menu_title"],
            width=self.settings["theme_info"]["menu_width"],
            height=self.settings["theme_info"]["menu_height"],
            theme=self.theme,
        )
        menu.enable()
        return menu

    def _play_game(self):
        """
        Callback function to start the game.

        :return: None
        """
        self.change_game_state = GameState.PLAYING

    def _stop_game(self):
        """
        Callback function to stop the game.

        :return: None
        """
        self.change_game_state = GameState.QUIT
