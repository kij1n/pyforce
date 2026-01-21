import pygame_menu
import pygame

from shared import GameState


class GameUI:
    def __init__(self, settings: dict):
        self.change_game_state = None
        self.settings = settings
        self.theme = self._create_theme()

        self.menu = self._create_menu()
        self._add_menu_buttons()

        self.pause_menu = self._create_pause_menu()
        self._add_pause_buttons()

    def render_pause(self, screen, events):
        screen.fill(self.settings["theme_info"]["background_color"])
        self.pause_menu.update(events)
        self.pause_menu.draw(screen)

    def render(self, screen, events):
        screen.fill(self.settings["theme_info"]["background_color"])
        self.menu.update(events)
        self.menu.draw(screen)

    def _create_pause_menu(self):
        menu = pygame_menu.Menu(
            self.settings["theme_info"]["pause_title"],
            width=self.settings["theme_info"]["menu_width"],
            height=self.settings["theme_info"]["menu_height"],
            theme=self.theme,
        )
        return menu

    def _add_pause_buttons(self):
        self.pause_menu.add.button(
            "Resume",
            self._play_game
        )
        self.pause_menu.add.button(
            "Quit",
            self._stop_game
        )

    def _add_menu_buttons(self):
        self.menu.add.button(
            "Play",
            self._play_game
        )
        self.menu.add.button(
            "Quit",
            self._stop_game
        )

    def _create_theme(self):
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
        menu = pygame_menu.Menu(
            self.settings["theme_info"]["menu_title"],
            width=self.settings["theme_info"]["menu_width"],
            height=self.settings["theme_info"]["menu_height"],
            theme=self.theme,
        )
        menu.enable()
        return menu

    def _play_game(self):
        self.change_game_state = GameState.PLAYING

    def _stop_game(self):
        self.change_game_state = GameState.QUIT