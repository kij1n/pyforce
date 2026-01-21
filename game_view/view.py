from shared import GameState
from .ui import GameUI
from .entity_renderer import *
from .sprite_loader import *
from .map_renderer import MapRenderer

from loguru import logger

import pymunk
import pymunk.pygame_util


class View:
    def __init__(self, settings: dict):
        logger.info("Initializing view...")

        self.settings = settings
        self.size = (settings["screen"]["size_x"], settings["screen"]["size_y"])

        pygame.display.set_caption(self.settings["title"])
        self.screen = pygame.display.set_mode(self.size)

        pygame.init()

        self.ui = GameUI(self.settings)
        self.sprite_loader = SpriteLoader(self.settings)
        self.entity_renderer = EntityRenderer()
        self.map_renderer = MapRenderer(self.size, self.settings)

    def render(self, player_pos, where_array: list[Where], bullets_set, debug_elements, game_state: GameState):
        if game_state == GameState.MENU:
            self.ui.change_game_state = game_state
            self.ui.render(self.screen, events=pygame.event.get())
            pygame.display.flip()
            return
        elif game_state == GameState.PAUSE:
            self.ui.change_game_state = game_state
            self.ui.render_pause(self.screen, events=pygame.event.get())
            pygame.display.flip()
            return

        self.map_renderer.render(player_pos, self.screen)
        self.entity_renderer.render(where_array, self.sprite_loader, self.screen, self.settings, player_pos)
        self.entity_renderer.render_bullets(bullets_set, self.sprite_loader, self.screen, self.settings, player_pos)

        # DEBUG DRAWING
        self._render_debug_info(player_pos, debug_elements)
        # DEBUG DRAWING

        pygame.display.flip()

    def _render_debug_info(self, player_pos, debug_elements):
        abs_camera_pos, rel_camera_pos = calc_camera_pos(self.settings, player_pos)
        vector = (rel_camera_pos[0] - abs_camera_pos[0], rel_camera_pos[1] - abs_camera_pos[1])

        if self.settings["debug"]["show_hitboxes"]:
            self._render_hitboxes(debug_elements.sim, vector)

        if self.settings["debug"]["show_patrol_paths"]:
            self._render_patrol_paths(debug_elements.patrol_paths, vector)

        if self.settings["debug"]["show_fps"]:
            pass

        if self.settings["debug"]["show_bbs"]:
            self._render_bbs(debug_elements.bbs)

    def _render_bbs(self, bbs):
        if bbs is None:
            return
        for rect in bbs:
            # we don't need to translate the rect, because it's already in relative coordinates
            pygame.draw.rect(self.screen, "red", rect)

    def _render_hitboxes(self, sim: pymunk.Space, vector: tuple[int, int]):
        draw_options = pymunk.pygame_util.DrawOptions(self.screen)
        draw_options.transform = pymunk.Transform.translation(vector[0], vector[1])
        sim.debug_draw(draw_options)

    def _render_patrol_paths(self, patrol_paths, vector):
        for path in patrol_paths:
            x1 = path.start[0]
            x2 = path.end[0]
            y = path.start[1]

            rect = pygame.Rect((x1 + vector[0], y + vector[1]), (x2 - x1, 10))

            pygame.draw.rect(self.screen, (255, 0, 0), rect)
