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
        self.input_handler = InputHandler()

        self.running = False

    def run(self):
        self.running = True

        initial_pos = self.model.physics.bodies_list[0].position if self.settings["debug"]["static_bodies_list"] else None

        while self.running:
            self.view.render(
                self.model.get_center_pos(),
                self.model.get_where(),
                self.model.physics.sim
            )

            # DEBUG
            if initial_pos is not None:
                if initial_pos != self.model.physics.bodies_list[0].position:
                    print("Position changed from", initial_pos, "to", self.model.physics.sim.bodies_list[0].position)



            self.model.physics.sim.step(self.settings["physics"]['time_step'])
            self.model.update()

            self.input_handler.handle(self)

            self.fps.tick(60)
