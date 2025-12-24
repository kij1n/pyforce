import pygame
import pytmx
import pyscroll
from .ui import GameUI


class View:
    def __init__(self, settings : dict):
        self.settings = settings
        self.size = (settings['size_x'], settings['size_y'])

        pygame.display.set_caption("Pyforce")
        self.screen = pygame.display.set_mode(self.size)

        pygame.init()

        self.ui = GameUI()
        self.map = MapLoader(self.size)

    def render_map(self, target):
        self.map.set_center(target)
        self.map.draw(self.screen)
        pygame.display.flip()


class MapLoader:
    def __init__(self, size : tuple[int, int]):
        tmx_data = pytmx.load_pygame("map.tmx")
        map_data = pyscroll.data.TiledMapData(tmx_data)

        self.map_layer = pyscroll.BufferedRenderer(map_data, size)
        self.group = pyscroll.PyscrollGroup(map_layer=self.map_layer)

    def add_sprite(self, sprite):
        self.group.add(sprite)

    def set_center(self, target):
        self.group.center(target)

    def draw(self, surface):
        self.group.draw(surface)