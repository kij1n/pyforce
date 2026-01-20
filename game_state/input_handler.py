import pygame

from game_data.entities.state_manager import Direction


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
            self.controller.model.move_player(Direction.LEFT)
        if keys[pygame.K_d]:
            self.controller.model.move_player(Direction.RIGHT)
        if keys[pygame.K_w] or keys[pygame.K_SPACE]:
            self.controller.model.move_player(Direction.UP)

        keys = pygame.mouse.get_pressed()

        if keys[0]:  # Left mouse button
            self.controller.model.player_shoot()
