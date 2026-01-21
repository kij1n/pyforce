from shared import Direction


class PatrolPath:
    def __init__(self, x_range, height):
        self.start = (x_range[0], height)
        self.end = (x_range[1], height)
        self.enemies = set()
        self.id = (x_range[0], x_range[1], height)

    def is_in(self, x, y_range: tuple[int, int]):
        return self.start[0] <= x <= self.end[0] and y_range[1] <= self.start[1] <= y_range[0]

    def is_at_end(self, x, direction):
        return (direction == Direction.LEFT and x - 40 <= self.start[0]) or (
            direction == Direction.RIGHT and x + 40 >= self.end[0]
        )

    def add_enemy(self, enemy):
        self.enemies.add(enemy)

    def remove_enemy(self, enemy):
        self.enemies.discard(enemy)
