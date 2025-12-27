import pygame

class InputHandler:
    def __init__(self, controller):
        self.controller = controller

    def handle(self):
        self.handle_events()
        self.handle_keys()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.controller.running = False

    def handle_keys(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_a]:
            self.controller.model.move_player('left')
        if keys[pygame.K_d]:
            self.controller.model.move_player('right')
        if keys[pygame.K_w]:
            self.controller.model.move_player('up')
