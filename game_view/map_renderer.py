"""
This module contains classes for loading and rendering the game map.
"""
import pytmx
import pyscroll
import os
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

    def render(self, target, screen):
        """
        Renders the map centered on the target position.

        :param target: The absolute world position to center the map on.
        :param screen: The pygame Surface to render onto.
        :return: None
        """
        self.map.draw(target, screen)


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

            tmx_data = pytmx.load_pygame(path)
            map_data = pyscroll.data.TiledMapData(tmx_data)

            self.map_layer = pyscroll.BufferedRenderer(map_data, size)
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

    def draw(self, target, surface):
        """
        Updates the map center and draws the map onto the given surface.

        :param target: The absolute world position to center the map on.
        :param surface: The pygame Surface to render onto.
        :return: None
        """
        self.set_center(target)
        self.group.draw(surface)
