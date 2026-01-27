import pygame

from .entity_renderer import convert_abs_to_rel, calc_camera_pos

class EffectsRenderer:
    def __init__(self, settings, screen):
        self.settings = settings
        self.screen = screen

    def render(self, effects, player_pos):
        cam_abs, cam_rel = calc_camera_pos(self.settings, player_pos)

        for effect in effects:
            pos = convert_abs_to_rel(effect.pos, cam_abs, cam_rel)
            rect = pygame.Rect(pos[0], pos[1], effect.size, effect.size)

            surface = pygame.Surface((effect.size, effect.size))
            surface.fill(effect.color)
            surface.set_alpha(effect.opacity * 255)

            self.screen.blit(surface, rect)

    def render_pickups(self, pickups, sprite_loader, player_pos):
        cam_abs, cam_rel = calc_camera_pos(self.settings, player_pos)

        for pickup in pickups:
            pos = convert_abs_to_rel(pickup.pos, cam_abs, cam_rel)

            p_type = pickup.info.type
            if p_type == "weapon":
                sprite_name = pickup.info.name
            else:
                sprite_name = f"pickup_{p_type}"

            sprite = sprite_loader.get_sprite(sprite_name)
            self.screen.blit(sprite.image, sprite.image.get_rect(center=pos))