import pygame
import pytmx
import pyscroll
import os
from .ui import GameUI

import pymunk
import pymunk.pygame_util


def convert_abs_to_rel(position, abs_camera_pos, rel_camera_pos):
    d_vector = (
        position[0] - abs_camera_pos[0],
        position[1] - abs_camera_pos[1]
    )
    relative_pos = (
        rel_camera_pos[0] + d_vector[0],
        rel_camera_pos[1] + d_vector[1]
    )
    return relative_pos

def calc_camera_pos(settings, player_pos):
    x = player_pos[0]
    y = player_pos[1]

    if x < settings["screen"]['size_x'] // 2:
        x = settings["screen"]['size_x'] // 2
    elif x > settings["map"]['size_x'] - settings["screen"]['size_x'] // 2:
        x = settings["map"]['size_x'] - settings["screen"]['size_x'] // 2
    if y < settings["screen"]['size_y'] // 2:
        y = settings["screen"]['size_y'] // 2
    elif y > settings["map"]['size_y'] - settings["screen"]['size_y'] // 2:
        y = settings["map"]['size_y'] - settings["screen"]['size_y'] // 2

    abs_camera_pos = (x, y)
    rel_camera_pos = (
        settings["screen"]['size_x'] // 2,
        settings["screen"]['size_y'] // 2
    )
    return abs_camera_pos, rel_camera_pos


class View:
    def __init__(self, settings : dict):
        self.settings = settings
        self.size = (settings["screen"]['size_x'], settings["screen"]['size_y'])

        pygame.display.set_caption(self.settings["title"])
        self.screen = pygame.display.set_mode(self.size)

        pygame.init()

        self.ui = GameUI()

        self.sprite_loader = SpriteLoader(self.settings)
        self.entity_renderer = EntityRenderer()
        self.map_renderer = MapRenderer(self.size, self.settings)

    def render(self, player_pos, where : list[tuple[tuple[int,int], str]], sim):
        self.map_renderer.render(player_pos, self.screen)
        self.entity_renderer.render(where, self.sprite_loader, self.screen, self.settings, player_pos)

        # --- DEBUG DRAWING START ---
        if self.settings["debug"]['show_hitboxes']:
            abs_camera_pos, rel_camera_pos = calc_camera_pos(self.settings, player_pos)
            vector = (
                rel_camera_pos[0] - abs_camera_pos[0],
                rel_camera_pos[1] - abs_camera_pos[1]
            )

            draw_options = pymunk.pygame_util.DrawOptions(self.screen)
            draw_options.transform = pymunk.Transform.translation(vector[0], vector[1])

            sim.debug_draw(draw_options)
        # --- DEBUG DRAWING END ---

        pygame.display.flip()


class EntityRenderer:
    @staticmethod
    def render(where : list[tuple[tuple[int,int], str]], sprite_loader, screen, settings, player_pos):
        abs_camera_pos, rel_camera_pos = calc_camera_pos(settings, player_pos)
        for entity in where:
            position, sprite_name = entity

            is_inverted = False
            inv_indicator = settings["sprites"]["inversion_indicator"]

            if sprite_name.startswith(inv_indicator):
                print("inverted")
                is_inverted = True
                sprite_name = sprite_name[len(inv_indicator):]

            sprite = sprite_loader.get_sprite(sprite_name)

            if is_inverted:
                image = sprite.invert_copy()
            else:
                image = sprite.image

            # calculate relative position
            relative_pos = convert_abs_to_rel(position, abs_camera_pos, rel_camera_pos)
            sprite.set_position(relative_pos)

            screen.blit(image, sprite.rect)


class MapRenderer:
    def __init__(self, size, settings : dict):
        self.map = MapLoader(size, settings)

    def render(self, target, screen):
        self.map.draw(target, screen)


class MapLoader:
    def __init__(self, size : tuple[int, int], settings : dict):
        self.settings = settings

        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(script_dir, settings["map"]["map_path"])

        if os.name == "nt":
            path = path.replace("/", "\\")

        tmx_data = pytmx.load_pygame(path)
        map_data = pyscroll.data.TiledMapData(tmx_data)

        self.map_layer = pyscroll.BufferedRenderer(map_data, size)
        self.group = pyscroll.PyscrollGroup(map_layer=self.map_layer)

    def set_center(self, target):
        target = (
            self.settings["screen"]['size_x'] // 2
            if target[0] < self.settings["screen"]['size_x'] // 2
            else target[0],
            self.settings["screen"]['size_y'] // 2
            if target[1] < self.settings["screen"]['size_y'] // 2
            else target[1]
        )
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

    def set_position(self, position):
        self.rect.center = position

    def invert_copy(self):
        return pygame.transform.flip(self.image, True, False)