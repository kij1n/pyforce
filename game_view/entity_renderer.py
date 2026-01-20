import pygame
from math import cos, sin, radians, sqrt
from shared import Where


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

    h_scr_x = settings['screen']['size_x'] // 2
    max_map_x = settings['map']['size_x'] - h_scr_x
    h_scr_y = settings['screen']['size_y'] // 2
    max_map_y = settings['map']['size_y'] - h_scr_y

    abs_camera_pos = (
        _clamp(h_scr_x, x, max_map_x),
        _clamp(h_scr_y, y, max_map_y)
    )

    rel_camera_pos = (
        settings["screen"]['size_x'] // 2,
        settings["screen"]['size_y'] // 2
    )
    return abs_camera_pos, rel_camera_pos


def calc_vector(abs_camera_pos, rel_camera_pos):
    vector = (
        rel_camera_pos[0] - abs_camera_pos[0],
        rel_camera_pos[1] - abs_camera_pos[1]
    )
    return vector


def _clamp(min_val, value, max_val):
    return max(min(value, max_val), min_val)


class EntityRenderer:
    def render_bullets(self, bullets_dict, sprite_loader, screen, settings, player_pos):
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
        sprite = sprite_loader.get_sprite(bullet.name)
        bullet_relative_pos = convert_abs_to_rel(
            position=pos,
            abs_camera_pos=abs_camera_pos,
            rel_camera_pos=rel_camera_pos
        )
        screen.blit(sprite.image, sprite.image.get_rect(center=bullet_relative_pos))

    def render(self, where_array: list[Where], sprite_loader, screen, settings, player_pos):
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

    def _handle_single_entity(self, abs_camera_pos, rel_camera_pos, where, sprite_loader, settings, screen):
        ent_relative_pos = convert_abs_to_rel(
            position=where.position,
            abs_camera_pos=abs_camera_pos,
            rel_camera_pos=rel_camera_pos
        )

        ent_sprite_name = where.name + '_' + where.state.value + str(where.sprite_index + 1)
        ent_sprite = sprite_loader.get_sprite(ent_sprite_name)  # Sprite instance, not pygame Surface
        if ent_sprite is None: return

        ent_surface, ent_rect = self._prepare_entity(ent_relative_pos, ent_sprite, where,
                                                     calc_vector(abs_camera_pos, rel_camera_pos))

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
            ent_data=(ent_surface, ent_rect)
        )

    def _handle_complex_entity(self, where, ent_relative_pos, sprite_loader, settings, screen, ent_data):
        arm_sprite_name = where.name + '_' + 'arm'
        arm_sprite = sprite_loader.get_sprite(arm_sprite_name)

        arm_surface = arm_rect = is_over = None
        if not where.is_dead:
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

        gun_surface = gun_rect = None

        if where.gun_name is not None and not where.is_dead:
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

        if is_over:
            screen.blit(ent_data[0], ent_data[1])
            screen.blit(arm_surface, arm_rect)
            if gun_surface: screen.blit(gun_surface, gun_rect)
        else:
            screen.blit(arm_surface, arm_rect)
            if gun_surface: screen.blit(gun_surface, gun_rect)
            screen.blit(ent_data[0], ent_data[1])

    @staticmethod
    def _calc_hand_position(arm_relative_pos, deg, hand_pos):
        length = sqrt(hand_pos[0] ** 2 + hand_pos[1] ** 2)
        pos = (
            arm_relative_pos[0] + length * cos(radians(deg - 90)),
            arm_relative_pos[1] - length * sin(radians(deg - 90))
        )

        return pos

    @staticmethod
    def _prepare_entity(ent_relative_pos, sprite, where, vector):
        img = sprite.image

        pos = (
            ent_relative_pos[0] + sprite.offset[0],
            ent_relative_pos[1] + sprite.offset[1]
        )

        where.hitbox.move_ip(vector)

        rect = img.get_rect(center=pos)
        rect.bottom = where.hitbox.bottom

        if where.inversion:
            img = pygame.transform.flip(img, True, False)

        return img, rect

    @staticmethod
    def _prepare_gun(hand_position, sprite, is_inverted, deg, handle_position_offset):
        is_on_left = False
        if deg > 180:
            deg = 360 - deg
            is_on_left = True

        img = pygame.transform.rotate(sprite.image, deg - 90)
        if is_on_left:
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

    @staticmethod
    def _prepare_arm(ent_relative_pos, sprite, is_inverted, deg, offset, rotation):
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
        if is_on_left:
            img = pygame.transform.flip(img, True, False)

        if is_inverted and deg not in [0, 180]:  # visual addition
            is_on_left = not is_on_left
        return img, img.get_rect(center=center_pos), is_on_left
