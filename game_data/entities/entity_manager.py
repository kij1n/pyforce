from player import Player
from enemy import Enemy

class EntityManager:
    def __init__(self):
        self.player = Player()
        self.enemies = {
            'enemy1': Enemy(),
            'enemy2': Enemy(),
        }