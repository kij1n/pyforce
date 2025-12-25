from .player import Player
from .enemy import Enemy

class EntityManager:
    def __init__(self, settings: dict):
        self.player = Player(settings)
        # self.enemies = {
        #     'enemy1': Enemy(settings),
        #     'enemy2': Enemy(settings),
        # }

    def get_player_pos(self):
        return self.player.position