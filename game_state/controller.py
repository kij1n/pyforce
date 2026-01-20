import pygame

from game_view import View
from game_data import Model

from .input_handler import InputHandler
from .json_manager import JSONManager

from loguru import logger


class Controller:
    def __init__(self):
        logger.info("Initializing controller...")

        self.json_manager = JSONManager()
        self.settings = self.json_manager.settings

        self.view = View(self.settings)
        self.model = Model(self.settings)

        self.fps = pygame.time.Clock()
        self.input_handler = InputHandler(self)

        self.running = False

    def run(self):
        self.running = True

        while self.running and self.model.game_not_lost():
            self.view.render(
                self.model.get_center_pos(),
                self.model.get_where_array(),
                self.model.get_bullets_dict(),
                self.model.debug_elements,
            )

            self.model.update(pygame.mouse.get_pos())

            self.input_handler.handle()

            self.fps.tick(self.settings["fps"])

        pygame.quit()
