"""
This module contains classes for loading and rendering the game map.
"""
import pytmx
import pyscroll
import os
import pygame
from loguru import logger


class MapRenderer:
    """
    The MapRenderer class provides a high-level interface for rendering the game map.

    Attributes:
        map (MapLoader): The MapLoader instance used for drawing the map.
    """

    def __init__(self, size, settings: dict):
        """
        Initializes the MapRenderer with the given size and settings.

        :param size: The size of the game window.
        :param settings: Dictionary containing game settings.
        :return: None
        """
        self.map = MapLoader(size, settings)

    def render(self, target, screen, sprite_loader):
        """
        Renders the map centered on the target position.

        :param target: The absolute world position to center the map on.
        :param screen: The pygame Surface to render onto.
        :param sprite_loader: The SpriteLoader instance to get the background from.
        :return: None
        """
        self.map.set_center(target)
        self.render_background(target, screen, sprite_loader)
        self.map.draw(target, screen)

    def render_background(self, target, screen, sprite_loader):
        """
        Renders the moving background.

        :param target: The absolute world position to center the map on.
        :param screen: The pygame Surface to render onto.
        :param sprite_loader: The SpriteLoader instance to get the background from.
        :return: None
        """
        bg_sprite = sprite_loader.get_sprite("map_background")
        if bg_sprite:
            self.map.draw_background(target, screen, bg_sprite.image)

class MapLoader:
    """
    The MapLoader class handles loading TMX map data and preparing it for rendering.

    Attributes:
        settings (dict): Dictionary containing game settings.
        map_layer (pyscroll.BufferedRenderer): The pyscroll renderer for the map.
        group (pyscroll.PyscrollGroup): The pyscroll group for managing map layers.
    """

    def __init__(self, size: tuple[int, int], settings: dict):
        """
        Initializes the MapLoader by loading the map file and setting up pyscroll.

        :param size: The size of the game window.
        :param settings: Dictionary containing game settings.
        :return: None
        """
        logger.info("Initializing map loader...")

        self.settings = settings
        self.map_layer = None
        self.group = None

        try:
            script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            path = os.path.join(script_dir, settings["map"]["map_path"])

            if os.name == "nt":
                path = path.replace("/", "\\")

            tmx_data = pytmx.util_pygame.load_pygame(path)
            map_data = pyscroll.data.TiledMapData(tmx_data)

            self.map_layer = pyscroll.BufferedRenderer(map_data, size, alpha=True)
            self.map_layer.clear_color = None
            self.group = pyscroll.PyscrollGroup(map_layer=self.map_layer)

        except FileNotFoundError:
            logger.error(f"Map file not found")
        except Exception as e:
            logger.error(f"Unexpected error loading map: {e}")

        logger.info("Map loaded successfully.")

    def set_center(self, target):
        """
        Sets the center of the map view based on the target position, with clamping for screen edges.

        :param target: The absolute world position to center the map on.
        :return: None
        """
        target = (
            self.settings["screen"]["size_x"] // 2 if target[0] < self.settings["screen"]["size_x"] // 2 else target[0],
            self.settings["screen"]["size_y"] // 2 if target[1] < self.settings["screen"]["size_y"] // 2 else target[1],
        )
        self.group.center(target)

    def draw_background(self, target, surface, background_image):
        """
        Calculates the parallax offset and draws the background onto the given surface.

        :param target: Position of the camera
        :param surface: The pygame Surface to render onto.
        :param background_image: The pygame Surface of the background.
        :return: None
        """
        map_width = self.map_layer.map_rect.width
        map_height = self.map_layer.map_rect.height
        screen_width = self.settings["screen"]["size_x"]
        screen_height = self.settings["screen"]["size_y"]
        bg_width = background_image.get_width()
        bg_height = background_image.get_height()

        camera_x = self.map_layer.view_rect.centerx
        camera_y = self.map_layer.view_rect.centery

        if map_width > screen_width:
            tx = (camera_x - screen_width / 2) / (map_width - screen_width)
            self._clamp(0, tx, 1)
        else:
            tx = 0.5

        if map_height > screen_height:
            ty = (camera_y - screen_height / 2) / (map_height - screen_height)
            self._clamp(0, ty, 1)
        else:
            ty = 0.5

        bx = -tx * (bg_width - screen_width) if bg_width > screen_width else (screen_width - bg_width) / 2
        by = -ty * (bg_height - screen_height) if bg_height > screen_height else (screen_height - bg_height) / 2

        surface.blit(background_image, (bx, by))

    @staticmethod
    def _clamp(min_value, value, max_value):
        return max(min_value, min(value, max_value))

    def draw(self, target, surface):
        """
        Updates the map center and draws the map onto the given surface.

        :param target: The absolute world position to center the map on.
        :param surface: The pygame Surface to render onto.
        :return: None
        """
        self.set_center(target)
        self.group.draw(surface)
