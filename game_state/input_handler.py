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
            # if event.type == pygame.MOUSEBUTTONDOWN:
            #     self.controller.model.player_shoot()


    def handle_keys(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_a]:
            self.controller.model.move_player('left')
        if keys[pygame.K_d]:
            self.controller.model.move_player('right')
        if keys[pygame.K_w] or keys[pygame.K_SPACE]:
            self.controller.model.move_player('up')

        keys = pygame.mouse.get_pressed()

        if keys[0]:  # Left mouse button
            self.controller.model.player_shoot()
