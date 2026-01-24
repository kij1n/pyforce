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