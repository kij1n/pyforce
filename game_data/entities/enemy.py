from .state_manager import StateManager
from .entity_helper import prepare_collision_box
from shared import *

class Enemy:
    def __init__(self, name: EnemyName, skin_color: SkinColor, settings : dict, pos, ent_id):
        self.name = name
        self.skin_color = skin_color  # flying or ground
        self.settings = settings

        self.body, self.shape, self.feet = prepare_collision_box(
            name.value, settings, pos, ent_id=ent_id
        )

        self.state_manager = StateManager(self)

        self.patrol_path = None
        self.aggro = False

        # action is not state
        self.current_action = None

    def get_sprite_qty(self, state):
        return len(self.settings["enemy_info"][self.name.value]["sprites_paths"][state])

    def get_position(self):
        return self.shape.body.position

    def get_collision_box(self):
        return [self.body, self.shape, self.feet]

    def is_patrolling(self):
        return self.patrol_path is not None

    def get_movement_direction(self):
        return self.state_manager.state.movement_direction

    def get_current_action(self) -> EnemyAction:
        return self.current_action

    def update_patrol_state(self):
        pass

    def change_action(self, action: EnemyAction):
        if self.current_action == action:
            return

        self.current_action = action
        if action in [EnemyAction.AGGRO, EnemyAction.PATROL]:
            self.state_manager.state.change_state("run", self.get_position(), self.body)