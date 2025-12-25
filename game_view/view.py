import pygame
import pytmx
import pyscroll
import os
from .ui import GameUI


class View:
    def __init__(self, settings : dict):
        self.settings = settings
        self.size = (settings["screen"]['size_x'], settings["screen"]['size_y'])

        pygame.display.set_caption("Pyforce")
        self.screen = pygame.display.set_mode(self.size)

        pygame.init()

        self.ui = GameUI()

        self.sprite_loader = SpriteLoader(self.settings)
        self.entity_renderer = EntityRenderer(self.settings)
        self.map_renderer = MapRenderer(self.size)

    def render(self, target):
        self.map_renderer.render(target, self.screen)

        pygame.display.flip()



class EntityRenderer:
    def __init__(self, settings : dict):
        pass


class MapRenderer:
    def __init__(self, size):
        self.map = MapLoader(size)

    def render(self, target, screen):
        self.map.set_center(target)
        self.map.draw(screen)
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


class SpriteLoader:
    def __init__(self, settings : dict):
        self.player = self.load_player(settings)
        self.enemies = {}

    @staticmethod
    def load_player(settings : dict):
        player = {}
        for sprite_type in settings["player_info"]["sprites_paths"].keys():
            for sprite_location in settings["player_info"]["sprites_paths"][sprite_type]:

                # create absolute path to the sprite
                script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                path = os.path.join(script_dir, sprite_location)

                if os.name == "nt":
                    path = path.replace("/", "\\")


                sprite = pygame.image.load(path).convert_alpha()
                if sprite_type not in player.keys():
                    player[sprite_type] = [sprite]
                else:
                    player[sprite_type].append(sprite)

        return player
