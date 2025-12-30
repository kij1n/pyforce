import pygame
import pytmx
import pyscroll
import os
from .ui import GameUI

from shared import Where
from math import cos, sin, radians, sqrt

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

    def render(self, player_pos, where_array: list[Where], sim):
        self.map_renderer.render(player_pos, self.screen)
        self.entity_renderer.render(where_array, self.sprite_loader, self.screen, self.settings, player_pos)

        # DEBUG DRAWING
        if self.settings["debug"]['show_hitboxes']:
            abs_camera_pos, rel_camera_pos = calc_camera_pos(self.settings, player_pos)
            vector = (
                rel_camera_pos[0] - abs_camera_pos[0],
                rel_camera_pos[1] - abs_camera_pos[1]
            )

            draw_options = pymunk.pygame_util.DrawOptions(self.screen)
            draw_options.transform = pymunk.Transform.translation(vector[0], vector[1])

            sim.debug_draw(draw_options)
        # DEBUG DRAWING

        pygame.display.flip()


class EntityRenderer:
    def render(self, where_array: list[Where], sprite_loader, screen, settings, player_pos):
        abs_camera_pos, rel_camera_pos = calc_camera_pos(settings, player_pos)
        for where in where_array:
            ent_relative_pos = convert_abs_to_rel(
                position=where.position,
                abs_camera_pos=abs_camera_pos,
                rel_camera_pos=rel_camera_pos
            )

            ent_sprite_name = where.name + '_'+ where.state + str(where.sprite_index + 1)
            ent_sprite = sprite_loader.get_sprite(ent_sprite_name)  # Sprite instance, not pygame Surface

            ent_surface, ent_rect = self._prepare_entity(ent_relative_pos, ent_sprite, where.inversion)

            arm_surface = arm_rect = None
            gun_surface = gun_rect = None
            is_over = None

            if where.arm_deg is not None:
                arm_sprite_name = where.name + '_' + 'arm'
                arm_sprite = sprite_loader.get_sprite(arm_sprite_name)

                arm_surface, arm_rect, is_over = self._prepare_arm(
                    ent_relative_pos=ent_relative_pos,
                    sprite=arm_sprite,
                    is_inverted=where.inversion,
                    deg=where.arm_deg,
                    offset=(
                        settings["sprites"]["arm_disp_vector_x"],
                        settings["sprites"]["arm_disp_vector_y"]
                    ),
                    rotation=(
                        settings["sprites"]["arm_rotation_x"],
                        settings["sprites"]["arm_rotation_y"]
                    ),
                )

                if where.gun_name is not None:
                    gun_sprite_name = where.gun_name
                    gun_sprite = sprite_loader.get_sprite(gun_sprite_name)

                    gun_surface, gun_rect = self._prepare_gun(
                        hand_position=self._calc_hand_position(
                            arm_rect.center, where.arm_deg,
                            (
                                settings['sprites']['arm_hand_x'],
                                settings['sprites']['arm_hand_y']
                            )
                        ),
                        sprite=gun_sprite,
                        deg=where.arm_deg,
                        is_inverted=where.inversion,
                        handle_position_offset=(
                            settings['sprites']['gun_handle_offset_x'],
                            settings['sprites']['gun_handle_offset_y']
                        )
                    )

            if is_over is not None:
                if is_over:
                    screen.blit(ent_surface, ent_rect)
                    screen.blit(arm_surface, arm_rect)
                    screen.blit(gun_surface, gun_rect)
                else:
                    screen.blit(arm_surface, arm_rect)
                    screen.blit(gun_surface, gun_rect)
                    screen.blit(ent_surface, ent_rect)
            else:
                screen.blit(ent_surface, ent_rect)

    @staticmethod
    def _calc_hand_position(arm_relative_pos, deg, hand_pos):
        length = sqrt(hand_pos[0] ** 2 + hand_pos[1] ** 2)
        pos = (
            arm_relative_pos[0] + length*cos(radians(deg - 90)),
            arm_relative_pos[1] - length*sin(radians(deg - 90))
        )

        return pos

    @staticmethod
    def _prepare_entity(ent_relative_pos, sprite, is_inverted):
        img = sprite.image
        rect = img.get_rect(center=ent_relative_pos)

        if is_inverted:
            img = pygame.transform.flip(img, True, False)

        return img, rect

    @staticmethod
    def _prepare_gun(hand_position, sprite, is_inverted, deg, handle_position_offset):
        is_on_left = False
        if deg > 180:
            deg = 360 - deg
            is_on_left = True

        img = pygame.transform.rotate(sprite.image, deg - 90)
        if is_on_left or is_inverted:
            img = pygame.transform.flip(img, True, False)

        rect = img.get_rect()

        if is_inverted:
            handle_position_offset = (
                handle_position_offset[0] * (-1),
                handle_position_offset[1]
            )

        rect.center = (
            hand_position[0] - handle_position_offset[0],
            hand_position[1] - handle_position_offset[1]
        )

        return img, rect


    def _prepare_arm(self, ent_relative_pos, sprite, is_inverted, deg, offset, rotation):
        is_on_left = False
        if deg > 180:
            deg = 360 - deg
            is_on_left = True

        length = sqrt(rotation[0] ** 2 + rotation[1] ** 2)
        vector = (  # vector of rotation point's position before and after rotation
            length * sin(radians(deg)),
            length * (cos(radians(deg)) - 1)
        )

        if is_on_left:
            vector = (
                vector[0] * (-1),
                vector[1]
            )
        if is_inverted:
            offset = (
                offset[0] * (-1), offset[1]
            )

        center_pos = (
            ent_relative_pos[0] + offset[0] + vector[0],
            ent_relative_pos[1] + offset[1] + vector[1]
        )

        img = pygame.transform.rotate(sprite.image, deg)
        if is_inverted or is_on_left:  # the image need to be rotated when one of them is true, but not if both
            img = pygame.transform.flip(img, True, False)

        if is_inverted and deg not in [0, 180]:  # visual addition
            is_on_left = not is_on_left
        return img, img.get_rect(center=center_pos), is_on_left


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

                if sprite_type == "arm":
                    sprite_name = "player_" + sprite_type
                elif sprite_type == 'guns':
                    delimiter = '\\' if os.name == "nt" else '/'
                    sprite_name = path.split('.')[0].split(delimiter)[-1]
                else:
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

    def rotate_copy(self, degrees):
        return pygame.transform.rotate(self.image, degrees)