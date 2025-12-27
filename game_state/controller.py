import pygame

from game_view import View
from game_data import Model

from .input_handler import InputHandler
from .json_manager import JSONManager

class Controller:
    def __init__(self):
        self.settings = JSONManager()
        self.settings = self.settings.s

        self.view = View(self.settings)
        self.model = Model(self.settings)

        self.fps = pygame.time.Clock()
        self.input_handler = InputHandler(self)

        self.running = False

    def run(self):
        self.running = True

        while self.running:
            self.view.render(
                self.model.get_center_pos(),
                self.model.get_where(),
                self.model.physics.sim
            )

            self.model.update()

            self.input_handler.handle()

            self.fps.tick(self.settings["fps"])

        pygame.quit()