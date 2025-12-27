from .player import Player
from .enemy import Enemy

class EntityManager:
    def __init__(self, settings: dict):
        self.player = Player(settings)
        self.enemies = {
            # 'enemy1': Enemy(settings),
            # 'enemy2': Enemy(settings),
        }

    def move_player(self, direction: str):
        self.player.state_manager.apply_force(direction)

    def get_player_pos(self):
        pos = self.player.get_position()
        return (
            pos[0], pos[1]
        )

    def get_where(self):
        where = [self.player.state_manager.get_where()]

        for enemy in self.enemies.values():
            where.append(enemy.state_manager.get_where(player_pos=self.player.get_position()))

        return where

    def get_entities(self):
        return [
            self.player,
            # self.enemies.values()
        ]