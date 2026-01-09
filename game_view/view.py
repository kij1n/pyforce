from .ui import GameUI
from .entity_renderer import *
from .sprite_loader import *
from .map_renderer import MapRenderer

from shared import Where

import pymunk
import pymunk.pygame_util


class View:
    def __init__(self, settings: dict):
        self.settings = settings
        self.size = (settings["screen"]['size_x'], settings["screen"]['size_y'])

        pygame.display.set_caption(self.settings["title"])
        self.screen = pygame.display.set_mode(self.size)

        pygame.init()

        self.ui = GameUI()

        self.sprite_loader = SpriteLoader(self.settings)
        self.entity_renderer = EntityRenderer()
        self.map_renderer = MapRenderer(self.size, self.settings)

    def render(self, player_pos, where_array: list[Where], bullets_set, sim):
        self.map_renderer.render(player_pos, self.screen)
        self.entity_renderer.render(where_array, self.sprite_loader, self.screen, self.settings, player_pos)
        self.entity_renderer.render_bullets(bullets_set, self.sprite_loader, self.screen, self.settings, player_pos)

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
