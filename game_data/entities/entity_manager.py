from .player import Player
from .enemy import Enemy

class EntityManager:
    def __init__(self, settings: dict):
        self.player = Player(settings)
        self.enemies = {
            # 'enemy1': Enemy(settings),
            # 'enemy2': Enemy(settings),
        }

    def get_player_pos(self):
        return self.player.position

    def get_where(self):
        where = [self.player.state_manager.get_where()]

        for enemy in self.enemies.values():
            where.append(enemy.state_manager.get_where())

        return where