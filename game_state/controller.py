import pygame

from game_view import View
from game_data import Model

from .input_handler import InputHandler

class Controller:
    def __init__(self):
        self.model = Model()
        self.view = View(self.model.settings.s)

        self.fps = pygame.time.Clock()
        self.input_handler = InputHandler()

        self.running = False

    def run(self):
        self.running = True

        while self.running:
            self.view.render(
                self.model.get_center_pos()
            )

            self.input_handler.handle(self)

            self.fps.tick(60)
