from pymunk import Vec2d

from shared import Direction


class Pickup:
    def __init__(self, pos: Vec2d, info, callback):
        self.pos = pos
        self.pos_range = (pos.y + info.movement_range[0], pos.y + info.movement_range[1])
        self.info = info
        self.callback = callback
        self.direction = Direction.UP

    def activate(self):
        args = None
        if self.info.type == "health":
            args = self.info.amount
        elif self.info.type == "weapon":
            args = self.info.name
        return self.callback(args)

    def update_pos(self, dt):
        if self.pos.y >= self.pos_range[1] or self.pos.y <= self.pos_range[0]:
            self._change_movement_direction()

        movement_speed = self.info.movement_speed
        self.pos = Vec2d(
            self.pos[0], self.pos[1] + movement_speed * dt * self._get_multiplier()
        )

    def _get_multiplier(self):
        return 1 if self.direction == Direction.DOWN else -1


    def _change_movement_direction(self):
        self.direction = Direction.DOWN if self.direction == Direction.UP else Direction.UP