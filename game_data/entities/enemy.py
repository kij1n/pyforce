from .state_manager import StateManager
from shared import SkinColor, EnemyName

class Enemy:
    def __init__(self, name: EnemyName, skin_color: SkinColor, settings : dict):
        self.name = name
        self.skin_color = skin_color  # flying or ground
        self.settings = settings
        self.state_manager = StateManager(self)
