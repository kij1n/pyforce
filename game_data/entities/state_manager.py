class StateManager:
    def __init__(self, entity):
        self.entity = entity
        self.state = "idle"

    def get_where(self, player_pos : tuple[int, int] = None) -> tuple[tuple[int,int], str]:
        if player_pos is None:
            # Player: center of screen, offset by half sprite size
            sprite_name = self.entity.get_sprite_name(self.state, 0)
            hitbox_x = self.entity.settings["player_info"]["hitbox_x"]
            hitbox_y = self.entity.settings["player_info"]["hitbox_y"]
            return (
                self.entity.settings["screen"]['size_x'] // 2,
                self.entity.settings["screen"]['size_y'] // 2,
            ), sprite_name
        else:
            return (
                self.entity.get_position(),
                self.entity.get_sprite_name(self.state, 0)
            ), self.entity.get_sprite_name(self.state, 0)