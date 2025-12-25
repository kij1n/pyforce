class StateManager:
    def __init__(self, entity):
        self.entity = entity
        self.state = "idle"

    def get_where(self) -> tuple[tuple[int,int], str]:
        return (
            self.entity.get_position(),
            self.entity.get_sprite_name(self.state, 0)
        )