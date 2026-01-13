import pymunk

class PatrolPath:
    def __init__(self, x_range, height):
        self.start = (x_range[0], height)
        self.end = (x_range[1], height)
        self.enemies = []

    def is_in(self, x, y_range: tuple[int, int]):
        return (
            self.start[0] <= x <= self.end[0] and
            y_range[0] <= self.start[1] <= y_range[1]
        )

    def is_at_end(self, x, direction):
        return (
            (direction == "left" and x <= self.start[0]) or
            (direction == "right" and x >= self.end[0])
        )
