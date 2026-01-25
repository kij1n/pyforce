from pymunk import Vec2d


class Pickup:
    def __init__(self, pos: Vec2d, info, callback):
        self.pos = pos
        self.info = info
        self.callback = callback

    def activate(self):
        args = None
        if self.info.type == "health":
            args = self.info.amount
        elif self.info.type == "weapon":
            args = self.info.name
        return self.callback(args)
