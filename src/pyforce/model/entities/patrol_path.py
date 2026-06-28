"""
This module contains the PatrolPath class which defines horizontal paths for enemy patrolling.
"""

import random

from shared import Direction


class PatrolPath:
    """
    The PatrolPath class represents a horizontal segment where enemies can patrol.

    Attributes:
        start (tuple): The starting (left) coordinates of the path.
        end (tuple): The ending (right) coordinates of the path.
        enemies (set): A set of enemies currently patrolling this path.
        id (tuple): A unique identifier for the path based on its coordinates.
    """

    def __init__(self, x_range, height, offset: int):
        """
        Initializes a PatrolPath with an X range and height.

        :param x_range: A tuple containing (start_x, end_x).
        :param height: The Y coordinate of the path.
        :return: None
        """
        self.offset = offset
        self.start = (x_range[0], height)
        self.end = (x_range[1], height)
        self.height = height
        self.enemies = set()
        self.id = (x_range[0], x_range[1], height)

    def is_in(self, x, y_range: tuple[int, int]):
        """
        Checks if a given coordinate is within the bounds of the patrol path.

        :param x: The X coordinate to check.
        :param y_range: A tuple containing (min_y, max_y).
        :return: True if the coordinate is within the path, False otherwise.
        """
        return self.start[0] <= x <= self.end[0] and y_range[1] <= self.start[1] <= y_range[0]

    def is_at_end(self, x, direction):
        """
        Checks if an entity at position X moving in a direction has reached the end of the path.

        :param x: The current X coordinate of the entity.
        :param direction: The Direction the entity is moving.
        :return: True if at the end of the path, False otherwise.
        """
        return (direction == Direction.LEFT and x - self.offset <= self.start[0]) or (
            direction == Direction.RIGHT and x + self.offset >= self.end[0]
        )

    def add_enemy(self, enemy):
        """
        Adds an enemy to the set of entities patrolling this path.

        :param enemy: The enemy entity to add.
        :return: None
        """
        self.enemies.add(enemy)

    def remove_enemy(self, enemy):
        """
        Removes an enemy from the set of entities patrolling this path.

        :param enemy: The enemy entity to remove.
        :return: None
        """
        self.enemies.discard(enemy)

    def collides_with_another(self, entity):
        bb1 = entity.shape.bb
        ents = [ent for ent in self.enemies if ent != entity]
        for ent in ents:
            bb2 = ent.shape.bb
            if bb1.intersects(bb2):
                return True

            try:  # we need to use try because of a bug in pymunk (crashes when there are no points)
                query = entity.shape.shapes_collide(ent.shape)
                return len(query.points) > 0
            except AssertionError:
                continue
        return False

    def get_random_x(self):
        return random.randint(self.start[0] + self.offset, self.end[0] - self.offset)
