import pygame

class InputHandler:
    def __init__(self):
        pass

    def handle(self, controller):
        self.handle_events(controller)

    def handle_events(self, controller):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                controller.running = False