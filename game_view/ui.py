"""
This module contains the GameUI class which handles the user interface and menus.
"""
import pygame_menu
from pygame_menu.locals import ALIGN_CENTER
import pygame
from functools import partial
from loguru import logger

from shared import GameState, GameMode, Difficulty


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

    # INFINITE:
    # enemies spawn constantly, some counter when reaches some level (depending on difficulty)
    # spawn random enemy in a random place.
    # high score is the number of enemies killed
    # with each enemy spawned their damage increases
    #
    # SPEEDRUN:
    # defeat all enemies as fast as possible. the number of enemies and their damage differs
    # with each difficulty
    # high score is time


    def __init__(self, settings: dict, screen):
        """
        Initializes the GameUI with settings and creates menus.

        :param settings: Dictionary containing game settings.
        :return: None
        """
        self.mouse_dict = {
            "mouse_left": "mouse1",
            "mouse_middle": "mouse3",
            "mouse_right": "mouse2"
        }
        self.screen = screen

        self.change_game_state = None
        self.selected_gamemode = None
        self.selected_difficulty = None
        self.username = "player"
        self.settings = settings
        self.theme = self._create_theme()

        self.menu = self._create_menu()
        self._add_menu_buttons()

        self.pause_menu = self._create_pause_menu()
        self._add_pause_buttons()

    def render_player_stats(self, stats):
        settings = self.settings["player_stats"]
        font = pygame.font.Font(self.theme.widget_font, settings["font_size"])
        text = [
            f"Username: {stats.username}",
            f"Enemies killed: {stats.killed_enemies}",
            f"Time elapsed: {stats.time_elapsed / 1000:.2f}s",
            f"Difficulty: {stats.difficulty.value}",
            f"Gamemode: {getattr(stats.game_mode, 'value', 'None')}"
        ]
        for line in text:
            text_surf = font.render(line, True, settings["font_color"])
            text_rect = text_surf.get_rect(center=(settings["position"][0], settings["position"][1] + settings["offset"][1] * text.index(line)))
            self.screen.blit(text_surf, text_rect)

    def render_pause(self, sprite_loader,events):
        """
        Renders the pause menu.

        :param sprite_loader:
        :param events: A list of pygame events to process.
        :return: None
        """
        self._render_background(self.screen, sprite_loader)
        self.pause_menu.update(events)
        self.pause_menu.draw(self.screen)

    def render(self, sprite_loader, events):
        """
        Renders the main menu.

        :param sprite_loader: SpriteLoader instance for loading sprites.
        :param screen: The pygame Surface to render onto.
        :param events: A list of pygame events to process.
        :return: None
        """
        self._render_background(self.screen, sprite_loader)
        self.menu.update(events)
        self.menu.draw(self.screen)

    @staticmethod
    def _render_background(screen, sprite_loader):
        sprite = sprite_loader.get_sprite("menu_background")
        screen_rect = screen.get_rect()
        rect = sprite.image.get_rect(center=screen_rect.center)
        screen.blit(sprite.image, rect)

    def _create_pause_menu(self):
        """
        Creates the pause menu instance.

        :return: A pygame_menu.Menu instance.
        """
        return self._create_submenu(self.settings["menu"]["pause_title"])

    def _add_pause_buttons(self):
        """
        Adds buttons to the pause menu.

        :return: None
        """
        self.pause_menu.add.button("Resume", self._play_game)
        self.pause_menu.add.button("Settings", self.settings_menu)
        self.pause_menu.add.button("Quit", self._stop_game)

    def _add_menu_buttons(self):
        """
        Adds buttons to the main menu.

        :return: None
        """
        # Gamemode sub-menu
        self.gamemode_menu = self._create_submenu("Select Gamemode")
        self.gamemode_menu.add.button("Speedrun", self._start_speedrun)
        self.gamemode_menu.add.button("Infinite", self._start_infinite)
        self.gamemode_menu.add.button("Back", pygame_menu.events.BACK)

        # Difficulty sub-menu
        self.difficulty_menu = self._create_submenu("Select Difficulty")
        self.difficulty_menu.add.button("Easy", self._select_easy)
        self.difficulty_menu.add.button("Normal", self._select_normal)
        self.difficulty_menu.add.button("Hard", self._select_hard)
        self.difficulty_menu.add.button("Back", pygame_menu.events.BACK)

        # Keybindings sub-menu
        self._create_key_binds_menu()

        # Settings sub-menu
        self.settings_menu = self._create_submenu("Settings")
        self.settings_menu.add.button("Keybindings", self.keybindings_menu)
        self.settings_menu.add.button("Back", pygame_menu.events.BACK)

        # username submenu
        self.username_menu = self._create_submenu("Enter Username")
        self.username_input = self.username_menu.add.text_input("", default="player", onchange=self._set_username)
        self.username_menu.add.button("Next", self.gamemode_menu)
        self.username_menu.add.button("Back", pygame_menu.events.BACK)

        self.menu.add.button("Play", self.username_menu)
        self.menu.add.button("Difficulty", self.difficulty_menu)
        self.menu.add.button("Settings", self.settings_menu)
        self.menu.add.button("Quit", self._stop_game)

    def _set_username(self, username):
        self.username = username

    def _select_easy(self):
        self.selected_difficulty = Difficulty.EASY
        self.difficulty_menu.reset(1)

    def _select_normal(self):
        self.selected_difficulty = Difficulty.NORMAL
        self.difficulty_menu.reset(1)

    def _select_hard(self):
        self.selected_difficulty = Difficulty.HARD
        self.difficulty_menu.reset(1)

    def _create_key_binds_menu(self):
        self.keybindings_menu = self._create_submenu("Keybindings")

        padding = self.settings["menu"]["frame_h"]["padding"]
        btn_padding = self.settings["menu"]["frame_h"]["button_padding"]
        margin = self.settings["menu"]["frame_h"]["margin"]
        font_size = self.settings["menu"]["keys_font_size"]
        keys_name_font_size = self.settings["menu"]["keys_name_font_size"]
        col1_w = self.settings["menu"]["frame_h"]["col1_w"]
        col2_w = self.settings["menu"]["frame_h"]["col2_w"]
        col3_w = self.settings["menu"]["frame_h"]["col3_w"]
        height = self.settings["menu"]["frame_h"]["height"]

        for bind in self.settings["key_bindings"]:
            key = alt = None
            bind_list = self._get_key_list(bind)
            action = bind_list[0]
            if len(bind_list) >= 2:
                key = bind_list[1]
            if len(bind_list) >= 3:
                alt = bind_list[2]

            row_frame = self.keybindings_menu.add.frame_h(
                width=col1_w + col2_w + col3_w,
                height=height,
                padding=padding,
                align=ALIGN_CENTER,
                font_size=font_size,
                margin=margin
            )

            c1_frame = self.keybindings_menu.add.frame_h(width=col1_w, height=height, padding=padding, margin=margin)
            label = self.keybindings_menu.add.label(action, font_size=keys_name_font_size, padding=btn_padding, margin=margin)
            c1_frame.pack(label, align=ALIGN_CENTER)

            c2_frame = self.keybindings_menu.add.frame_h(width=col2_w, height=height, padding=padding, margin=margin)
            btn = self.keybindings_menu.add.button(key, font_size=font_size, padding=btn_padding, margin=margin)

            callback = partial(self.start_rebinding, btn, action, 0)
            btn.set_onreturn(callback)

            c2_frame.pack(btn, align=ALIGN_CENTER)

            c3_frame = self.keybindings_menu.add.frame_h(width=col3_w, height=height, padding=padding, margin=margin)
            btn_alt = self.keybindings_menu.add.button(alt, font_size=font_size, padding=btn_padding, margin=margin)

            callback = partial(self.start_rebinding, btn_alt, action, 1)
            btn_alt.set_onreturn(callback)

            c3_frame.pack(btn_alt, align=ALIGN_CENTER)

            row_frame.pack(c1_frame)
            row_frame.pack(c2_frame)
            row_frame.pack(c3_frame)

        self.keybindings_menu.add.button("Back", pygame_menu.events.BACK)

    def start_rebinding(self, widget, action, index):
        """
        Waits for a keypress/click and updates the binding.
        :param widget: The Button object that was clicked
        :param action: The string name of the action (e.g., "jump")
        :param index: 0 for a primary key, 1 for an alt key
        """
        self._render_choice_overlay(action)

        new_bind = self._listen_for_new_bind()

        if new_bind:
            bind_list = self.settings["key_bindings"][action]
            while len(bind_list) <= index:
                bind_list.append(None)

            bind_list[index] = new_bind

            display_text = self.mouse_dict.get(new_bind, new_bind)
            widget.set_title(display_text)
            logger.info(f"Keybinding for '{action}' updated to '{display_text}'.")

    @staticmethod
    def _listen_for_new_bind():
        listening = True
        new_bind = None

        while listening:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

                # A. Keyboard Input
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE:
                        # Cancel rebinding on Escape
                        listening = False
                    else:
                        # Get string name (e.g., "space", "return")
                        new_bind = pygame.key.name(event.key)
                        listening = False

                # B. Mouse Input
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # Map Pygame IDs to your Strings
                    mouse_map = {1: "mouse_left", 2: "mouse_middle", 3: "mouse_right"}
                    if event.button in mouse_map:
                        new_bind = mouse_map[event.button]
                        listening = False
        return new_bind

    def _render_choice_overlay(self, action):
        settings = self.settings["menu"]

        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill(settings["overlay_color"])
        self.screen.blit(overlay, (0, 0))

        font_path = self.theme.widget_font

        font = pygame.font.Font(font_path, settings["bind_change_font_size"])
        text = f"Press a new key for '{action}'..."
        text_surf = font.render(text, True, settings["theme_info"]["font_color"])

        font = pygame.font.Font(font_path, settings["bind_cancel_font_size"])
        text = "Press backspace to cancel."
        text_surf2 = font.render(text, True, settings["theme_info"]["font_color"])

        text_rect = text_surf.get_rect(center=self.screen.get_rect().center)
        self.screen.blit(text_surf, text_rect)

        text_rect2 = text_surf2.get_rect(center=(self.screen.get_rect().centerx, self.screen.get_rect().centery + settings["bind_cancel_offset"][1]))
        self.screen.blit(text_surf2,text_rect2)

        pygame.display.flip()

    def _get_key_list(self, action: str):
        binds = self.settings["key_bindings"][action].copy()
        output = [action]

        if len(binds) >= 1:
            if binds[0].startswith("mouse_"):
                binds[0] = self.mouse_dict[binds[0]]
            output.append(binds[0])
        if len(binds) >= 2:
            if binds[1].startswith("mouse_"):
                binds[1] = self.mouse_dict[binds[1]]
            output.append(binds[1])

        return output

    def _create_submenu(self, title):
        """
        Creates a submenu instance with default settings.

        :param title: Title of the submenu.
        :return: A pygame_menu.Menu instance.
        """
        return pygame_menu.Menu(
            title,
            width=self.settings["menu"]["submenu_width"],
            height=self.settings["menu"]["submenu_height"],
            theme=self.theme,
            mouse_motion_selection=self.settings["menu"]["mouse_motion_selection"],
        )

    def _start_speedrun(self):
        """
        Callback function to start the game in speedrun mode.

        :return: None
        """
        self.selected_gamemode = GameMode.SPEEDRUN
        self._play_game()

    def _start_infinite(self):
        """
        Callback function to start the game in infinite mode.

        :return: None
        """
        self.selected_gamemode = GameMode.INFINITE
        self._play_game()

    def _create_theme(self):
        """
        Creates the theme for the menus.

        :return: A pygame_menu.Theme instance.
        """
        settings = self.settings["menu"]["theme_info"]
        theme = pygame_menu.Theme(
            background_color=settings["menu_background_color"],
            title_font=pygame_menu.font.FONT_MUNRO,
            title_font_shadow=settings["font_shadow"],
            widget_padding=settings["widget_padding"],
            widget_font=pygame_menu.font.FONT_MUNRO,
            widget_font_color=settings["font_color"],
        )
        return theme

    def _create_menu(self):
        """
        Creates the main menu instance.

        :return: A pygame_menu.Menu instance.
        """
        menu = self._create_submenu(self.settings["menu"]["menu_title"])
        menu.enable()
        return menu

    def _play_game(self):
        """
        Callback function to start the game.

        :return: None
        """
        logger.info("Starting game...")
        self.change_game_state = GameState.PLAYING

    def _stop_game(self):
        """
        Callback function to stop the game.

        :return: None
        """
        self.change_game_state = GameState.QUIT
