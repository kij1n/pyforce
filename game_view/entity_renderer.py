"""
This module contains the EntityRenderer class and helper functions for rendering game entities.
"""
import pygame
from math import cos, sin, radians, sqrt

from loguru import logger

from shared import Where


def convert_abs_to_rel(position, abs_camera_pos, rel_camera_pos):
    """
    Converts absolute world coordinates to screen-relative coordinates based on the camera position.

    :param position: The absolute world position to convert.
    :param abs_camera_pos: The absolute position of the camera in the world.
    :param rel_camera_pos: The relative position of the camera on the screen.
    :return: A tuple representing the screen-relative position.
    """
    d_vector = (position[0] - abs_camera_pos[0], position[1] - abs_camera_pos[1])
    relative_pos = (rel_camera_pos[0] + d_vector[0], rel_camera_pos[1] + d_vector[1])
    return relative_pos


def calc_camera_pos(settings, player_pos):
    """
    Calculates the absolute and relative camera positions based on the player's position and screen settings.

    :param settings: Dictionary containing game settings.
    :param player_pos: The current absolute position of the player.
    :return: A tuple containing (abs_camera_pos, rel_camera_pos).
    """
    x = player_pos[0]
    y = player_pos[1]

    h_scr_x = settings["screen"]["size_x"] // 2
    max_map_x = settings["map"]["size_x"] - h_scr_x
    h_scr_y = settings["screen"]["size_y"] // 2
    max_map_y = settings["map"]["size_y"] - h_scr_y

    abs_camera_pos = (_clamp(h_scr_x, x, max_map_x), _clamp(h_scr_y, y, max_map_y))

    rel_camera_pos = (settings["screen"]["size_x"] // 2, settings["screen"]["size_y"] // 2)
    return abs_camera_pos, rel_camera_pos


def calc_vector(abs_camera_pos, rel_camera_pos):
    """
    Calculates the translation vector from absolute world coordinates to screen-relative coordinates.

    :param abs_camera_pos: The absolute position of the camera.
    :param rel_camera_pos: The relative position of the camera on the screen.
    :return: A tuple representing the translation vector.
    """
    vector = (rel_camera_pos[0] - abs_camera_pos[0], rel_camera_pos[1] - abs_camera_pos[1])
    return vector


def _clamp(min_val, value, max_val):
    return max(min(value, max_val), min_val)


class EntityRenderer:
    """
    The EntityRenderer class provides methods for rendering
    various game entities, including players, enemies, and bullets.
    """

    def render_bullets(self, bullets_dict, sprite_loader, screen, settings, player_pos):
        """
        Renders all active bullets.

        :param bullets_dict: A dictionary mapping bullet objects to their physics shapes.
        :param sprite_loader: The SpriteLoader instance to use for getting bullet sprites.
        :param screen: The pygame Surface to render onto.
        :param settings: Dictionary containing game settings.
        :param player_pos: The current absolute position of the player.
        :return: None
        """
        abs_camera_pos, rel_camera_pos = calc_camera_pos(settings, player_pos)
        for bullet, shape in bullets_dict.items():
            self._handle_single_bullet(
                abs_camera_pos=abs_camera_pos,
                rel_camera_pos=rel_camera_pos,
                bullet=bullet,
                pos=shape.body.position,
                sprite_loader=sprite_loader,
                screen=screen,
            )

    @staticmethod
    def _handle_single_bullet(abs_camera_pos, rel_camera_pos, bullet, pos, sprite_loader, screen):
        """
        Renders a single bullet.

        :param abs_camera_pos: The absolute position of the camera.
        :param rel_camera_pos: The relative position of the camera on the screen.
        :param bullet: The bullet object to render.
        :param pos: The absolute position of the bullet.
        :param sprite_loader: The SpriteLoader instance.
        :param screen: The pygame Surface to render onto.
        :return: None
        """
        sprite = sprite_loader.get_sprite(bullet.name)
        bullet_relative_pos = convert_abs_to_rel(
            position=pos, abs_camera_pos=abs_camera_pos, rel_camera_pos=rel_camera_pos
        )
        screen.blit(sprite.image, sprite.image.get_rect(center=bullet_relative_pos))

    def render(self, where_array: list[Where], sprite_loader, screen, settings, player_pos):
        """
        Renders all game entities and their health bars.

        :param where_array: A list of Where objects containing entity rendering information.
        :param sprite_loader: The SpriteLoader instance.
        :param screen: The pygame Surface to render onto.
        :param settings: Dictionary containing game settings.
        :param player_pos: The current absolute position of the player.
        :return: None
        """
        abs_camera_pos, rel_camera_pos = calc_camera_pos(settings, player_pos)
        for where in where_array:
            self._handle_single_entity(
                abs_camera_pos=abs_camera_pos,
                rel_camera_pos=rel_camera_pos,
                where=where,
                sprite_loader=sprite_loader,
                settings=settings,
                screen=screen,
            )
            self._handle_health_bar(where, screen, abs_camera_pos, rel_camera_pos, settings)

    @staticmethod
    def _handle_health_bar(where, screen, abs_camera_pos, rel_camera_pos, settings):
        """
        Renders the health bar for a single entity.

        :param where: The Where object containing entity information.
        :param screen: The pygame Surface to render onto.
        :param abs_camera_pos: The absolute position of the camera.
        :param rel_camera_pos: The relative position of the camera on the screen.
        :param settings: Dictionary containing game settings.
        :return: None
        """
        ent_relative_pos = convert_abs_to_rel(
            position=where.position, abs_camera_pos=abs_camera_pos, rel_camera_pos=rel_camera_pos
        )

        offset = settings["health_bar_info"]["offset"]
        height = settings["health_bar_info"]["height"]
        width = settings["health_bar_info"]["width"]
        color = settings["health_bar_info"]["color"]
        back_color = settings["health_bar_info"]["background_color"]

        pos = (ent_relative_pos[0] + offset[0], ent_relative_pos[1] + offset[1])

        health_bar_rect_full = pygame.Rect((0, 0), (width, height))
        health_bar_rect_full.center = pos

        health_bar_rect_filled = pygame.Rect((0, 0), (width * where.health_percent, height))
        health_bar_rect_filled.center = health_bar_rect_full.center
        health_bar_rect_filled.left = health_bar_rect_full.left

        pygame.draw.rect(screen, back_color, health_bar_rect_full)
        pygame.draw.rect(screen, color, health_bar_rect_filled)

    def _handle_single_entity(self, abs_camera_pos, rel_camera_pos, where, sprite_loader, settings, screen):
        """
        Handles the rendering process for a single entity.

        :param abs_camera_pos: The absolute position of the camera.
        :param rel_camera_pos: The relative position of the camera on the screen.
        :param where: The Where object containing entity information.
        :param sprite_loader: The SpriteLoader instance.
        :param settings: Dictionary containing game settings.
        :param screen: The pygame Surface to render onto.
        :return: None
        """
        ent_relative_pos = convert_abs_to_rel(
            position=where.position, abs_camera_pos=abs_camera_pos, rel_camera_pos=rel_camera_pos
        )

        ent_sprite_name = where.name + "_" + where.state.value + str(where.sprite_index + 1)
        ent_sprite = sprite_loader.get_sprite(ent_sprite_name)  # Sprite instance, not pygame Surface
        if ent_sprite is None:
            return

        ent_surface, ent_rect = self._prepare_entity(
            ent_relative_pos, ent_sprite, where, calc_vector(abs_camera_pos, rel_camera_pos)
        )

        if where.arm_deg is None:
            screen.blit(ent_surface, ent_rect)
            return

        # if we arrived here, it's a player
        self._handle_complex_entity(
            where=where,
            ent_relative_pos=ent_relative_pos,
            sprite_loader=sprite_loader,
            settings=settings,
            screen=screen,
            ent_data=(ent_surface, ent_rect),
        )

    def _handle_complex_entity(self, where, ent_relative_pos, sprite_loader, settings, screen, ent_data):
        """
        Handles the rendering process for a complex entity (e.g., player with arm and gun).

        :param where: The Where object containing entity information.
        :param ent_relative_pos: The relative position of the entity on the screen.
        :param sprite_loader: The SpriteLoader instance.
        :param settings: Dictionary containing game settings.
        :param screen: The pygame Surface to render onto.
        :param ent_data: A tuple containing the entity's surface and rect.
        :return: None
        """
        arm_sprite_name = where.name + "_" + "arm"
        arm_sprite = sprite_loader.get_sprite(arm_sprite_name)

        arm_surface = arm_rect = is_over = None
        if not where.is_dead:
            arm_surface, arm_rect, is_over = self._prepare_arm(
                ent_relative_pos=ent_relative_pos,
                sprite=arm_sprite,
                is_inverted=where.inversion,
                deg=where.arm_deg,
                offset=(settings["sprites"]["arm_disp_vector_x"], settings["sprites"]["arm_disp_vector_y"]),
                rotation=(settings["sprites"]["arm_rotation_x"], settings["sprites"]["arm_rotation_y"]),
            )

        gun_surface = gun_rect = None

        if where.gun_name is not None and not where.is_dead:
            gun_sprite_name = where.gun_name
            gun_sprite = sprite_loader.get_sprite(gun_sprite_name)

            gun_surface, gun_rect = self._prepare_gun(
                hand_position=self._calc_hand_position(
                    arm_rect.center,
                    where.arm_deg,
                    (settings["sprites"]["arm_hand_x"], settings["sprites"]["arm_hand_y"]),
                ),
                sprite=gun_sprite,
                deg=where.arm_deg,
                is_inverted=where.inversion,
                handle_position_offset=(
                    settings["sprites"]["gun_handle_offset_x"],
                    settings["sprites"]["gun_handle_offset_y"],
                ),
            )

        gun_data = (gun_surface, gun_rect)
        arm_data = (arm_surface, arm_rect)
        self._render_complex_entity(screen, ent_data, arm_data, gun_data, is_over)

    @staticmethod
    def _render_complex_entity(screen, ent_data, arm_data, gun_data, is_over):
        """
        Renders the parts of a complex entity in the correct order.

        :param screen: The pygame Surface to render onto.
        :param ent_data: A tuple containing the entity's surface and rect.
        :param arm_data: A tuple containing the arm's surface and rect.
        :param gun_data: A tuple containing the gun's surface and rect.
        :param is_over: Boolean indicating if the arm is over the entity.
        :return: None
        """
        if is_over:
            screen.blit(ent_data[0], ent_data[1])
            if None not in gun_data:
                screen.blit(gun_data[0], gun_data[1])
            if None not in arm_data:
                screen.blit(arm_data[0], arm_data[1])
        else:
            if None not in arm_data:
                screen.blit(arm_data[0], arm_data[1])
            if None not in gun_data:
                screen.blit(gun_data[0], gun_data[1])
            screen.blit(ent_data[0], ent_data[1])

    @staticmethod
    def _calc_hand_position(arm_relative_pos, deg, hand_pos):
        """
        Calculates the screen position of the hand on an arm.

        :param arm_relative_pos: The relative position of the arm.
        :param deg: The rotation angle of the arm.
        :param hand_pos: The local position of the hand on the arm sprite.
        :return: A tuple representing the screen position of the hand.
        """
        length = sqrt(hand_pos[0] ** 2 + hand_pos[1] ** 2)
        pos = (  # subtract because 0deg is pointing down
            arm_relative_pos[0] + length * cos(radians(deg - 90)),
            arm_relative_pos[1] - length * sin(radians(deg - 90)),
        )
        return pos

    @staticmethod
    def _prepare_entity(ent_relative_pos, sprite, where, vector):
        """
        Prepares the entity's surface and rect for rendering.

        :param ent_relative_pos: The relative position of the entity on the screen.
        :param sprite: The Sprite instance for the entity.
        :param where: The Where object containing entity information.
        :param vector: The translation vector for the camera.
        :return: A tuple containing (surface, rect).
        """
        img = sprite.image

        pos = (ent_relative_pos[0] + sprite.offset[0], ent_relative_pos[1] + sprite.offset[1])

        where.hitbox.move_ip(vector)

        rect = img.get_rect(center=pos)
        rect.bottom = where.hitbox.bottom

        if where.inversion:
            img = pygame.transform.flip(img, True, False)

        return img, rect

    @staticmethod
    def _prepare_gun(hand_position, sprite, is_inverted, deg, handle_position_offset):
        """
        Prepares the gun's surface and rect for rendering.

        :param hand_position: The screen position of the hand holding the gun.
        :param sprite: The Sprite instance for the gun.
        :param is_inverted: Boolean indicating if the gun should be flipped.
        :param deg: The rotation angle of the gun, in degrees.
        :param handle_position_offset: The offset of the handle on the gun sprite.
        :return: A tuple containing (surface, rect).
        """
        is_on_left = False
        if deg > 180:
            deg = 360 - deg
            is_on_left = True

        img = pygame.transform.rotate(sprite.image, deg - 90)
        if is_on_left:
            img = pygame.transform.flip(img, True, False)

        rect = img.get_rect()

        if is_inverted:
            handle_position_offset = (handle_position_offset[0] * (-1), handle_position_offset[1])

        rect.center = (hand_position[0] - handle_position_offset[0], hand_position[1] - handle_position_offset[1])

        return img, rect

    @staticmethod
    def _prepare_arm(ent_relative_pos, sprite, is_inverted, deg, offset, rotation):
        """
        Prepares the arm's surface and rect for rendering.

        :param ent_relative_pos: The relative position of the entity on the screen.
        :param sprite: The Sprite instance for the arm.
        :param is_inverted: Boolean indicating if the arm should be flipped.
        :param deg: The rotation angle of the arm, in degrees.
        :param offset: The displacement vector for the arm's position.
        :param rotation: The rotation point for the arm.
        :return: A tuple containing (surface, rect, is_on_left).
        """
        is_on_left = False
        if deg > 180:
            deg = 360 - deg
            is_on_left = True

        length = sqrt(rotation[0] ** 2 + rotation[1] ** 2)
        vector = (  # vector of rotation point's position before and after rotation
            length * sin(radians(deg)),
            length * (cos(radians(deg)) - 1),
        )

        if is_on_left:
            vector = (vector[0] * (-1), vector[1])
        if is_inverted:
            offset = (offset[0] * (-1), offset[1])

        center_pos = (ent_relative_pos[0] + offset[0] + vector[0], ent_relative_pos[1] + offset[1] + vector[1])

        img = pygame.transform.rotate(sprite.image, deg)
        if is_on_left:
            img = pygame.transform.flip(img, True, False)

        if is_inverted and deg not in [0, 180]:  # visual addition
            is_on_left = not is_on_left
        return img, img.get_rect(center=center_pos), is_on_left
