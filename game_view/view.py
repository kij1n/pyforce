import pygame
import pytmx
import pyscroll
import os
from .ui import GameUI

import pymunk
import pymunk.pygame_util


class View:
    def __init__(self, settings : dict):
        self.settings = settings
        self.size = (settings["screen"]['size_x'], settings["screen"]['size_y'])

        pygame.display.set_caption("Pyforce")
        self.screen = pygame.display.set_mode(self.size)

        pygame.init()

        self.ui = GameUI()

        self.sprite_loader = SpriteLoader(self.settings)
        self.entity_renderer = EntityRenderer()
        self.map_renderer = MapRenderer(self.size, self.settings)

    def render(self, target, where : list[tuple[tuple[int,int], str]], sim):
        self.map_renderer.render(target, self.screen)
        self.entity_renderer.render(where, self.sprite_loader, self.screen)

        # DEBUG: draw physics shapes
        temp_sim = sim


        # draw_options = pymunk.pygame_util.DrawOptions(self.screen)
        # sim.debug_draw(draw_options)

        pygame.display.flip()


class EntityRenderer:
    @staticmethod
    def render(where : list[tuple[tuple[int,int], str]], sprite_loader, screen):
        for entity in where:
            position, sprite_name = entity
            sprite = sprite_loader.get_sprite(sprite_name)
            sprite.rect.center = position

            # sprite.move(position)
            screen.blit(sprite.image, sprite.rect)

class MapRenderer:
    def __init__(self, size, settings : dict):
        self.map = MapLoader(size, settings)

    def render(self, target, screen):
        self.map.draw(target, screen)


class MapLoader:
    def __init__(self, size : tuple[int, int], settings : dict):
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(script_dir, settings["map"]["map_path"])

        if os.name == "nt":
            path = path.replace("/", "\\")


        tmx_data = pytmx.load_pygame(path)
        map_data = pyscroll.data.TiledMapData(tmx_data)

        self.map_layer = pyscroll.BufferedRenderer(map_data, size)
        self.group = pyscroll.PyscrollGroup(map_layer=self.map_layer)

    def set_center(self, target):
        self.group.center(target)

    def draw(self, target, surface):
        self.set_center(target)
        self.group.draw(surface)


class SpriteLoader:
    def __init__(self, settings : dict):
        self.sprites = (
            self.load_player(settings) |
            self.load_enemies(settings)
        )

    def load_player(self, settings : dict):
        player = {}
        for sprite_type in settings["player_info"]["sprites_paths"].keys():
            index = 1
            for sprite_location in settings["player_info"]["sprites_paths"][sprite_type]:
                path = self._get_path(sprite_location)

                image = pygame.image.load(path).convert_alpha()
                sprite = Sprite(image)

                sprite_name = "player_" + sprite_type + str(index)
                index += 1

                player[sprite_name] = sprite
        return player

    def load_enemies(self, settings : dict):
        return {}

    def get_sprite(self, sprite_name):
        return self.sprites[sprite_name]

    @staticmethod
    def _get_path(sprite_location):
        # create absolute path to the sprite
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(script_dir, sprite_location)

        if os.name == "nt":
            path = path.replace("/", "\\")

        return path


class Sprite(pygame.sprite.Sprite):
    def __init__(self, image: pygame.Surface):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()

    def move(self, position: tuple[int, int]):
        dx = position[0] - self.rect.centerx
        dy = position[1] - self.rect.centery
        self.rect = self.rect.move(dx, dy)
