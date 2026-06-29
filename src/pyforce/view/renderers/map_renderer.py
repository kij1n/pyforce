"""
This module contains classes for loading and rendering the game map.
"""

from pyforce.view.loaders import MapLoader


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
