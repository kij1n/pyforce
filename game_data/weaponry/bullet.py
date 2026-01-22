"""
This module contains the Bullet class which represents a projectile in the game.
"""
from math import cos, radians, sin
from pymunk import Body, Circle, ShapeFilter
from shared import BasicBulletInfo


class Bullet:
    """
    The Bullet class manages the state and physics of a single projectile.

    Attributes:
        id (int): Unique identifier for the bullet.
        start_pos (Vec2d): The initial position of the bullet.
        pos (Vec2d): Current position of the bullet.
        reach (float): Maximum distance the bullet can travel.
        damage (int): Damage dealt by the bullet.
        name (str): Type name of the bullet.
        timer (int): Lifespan counter.
        has_collided (bool): Whether the bullet has hit something.
        body (pymunk.Body): Physics body of the bullet.
        shape (pymunk.Circle): Physics shape of the bullet.
    """

    def __init__(self, info: BasicBulletInfo, arm_deg, ammo, settings):
        """
        Initializes a Bullet instance and its physical representation.

        :param info: Basic information about the bullet.
        :param arm_deg: The angle at which the bullet is fired.
        :param ammo: The Ammo instance defining projectile properties.
        :param settings: Dictionary containing game settings.
        :return: None
        """
        self.id = info.id
        self.start_pos = info.start_pos
        self.pos = info.start_pos
        self.reach = info.reach
        self.damage = info.damage
        self.name = info.name
        self.timer = 0
        self.has_collided = False

        self.body = self._create_body_bullet(ammo)
        self.shape = self._create_shape_bullet(ammo, settings)
        self._apply_bullet_impulse(arm_deg, ammo)

    def __hash__(self):
        """
        Returns the hash of the bullet based on its unique ID.

        :return: Hash value.
        """
        return hash(self.id)

    def __eq__(self, other):
        """
        Checks equality between two Bullet instances.

        :param other: The other object to compare.
        :return: True if IDs match, False otherwise.
        """
        if not isinstance(other, Bullet):
            return NotImplemented
        return self.id == other.id

    def __del__(self):
        del self

    def _create_body_bullet(self, ammo):
        """
        Creates the pymunk Body for the bullet.

        :param ammo: The Ammo instance.
        :return: A pymunk.Body instance.
        """
        body = Body(mass=ammo.bullet_mass, moment=float("inf"), body_type=Body.DYNAMIC)
        body.position = self.pos
        return body

    def _create_shape_bullet(self, ammo, settings):
        """
        Creates the pymunk Shape for the bullet.

        :param ammo: The Ammo instance.
        :param settings: Dictionary containing game settings.
        :return: A pymunk.Circle instance.
        """
        shape = Circle(self.body, ammo.bullet_radius)
        shape.collision_type = settings["physics"]["collision_types"]["bullet"]
        shape.filter = ShapeFilter(
            categories=settings["physics"]["collision_categories"]["player_bullet"],
            mask=settings["physics"]["collision_masks"]["player_bullet"],
        )
        shape.bullet = self
        return shape

    def _apply_bullet_impulse(self, angle, ammo):
        """
        Applies an initial impulse to the bullet body based on firing angle and velocity.

        :param angle: The firing angle in degrees.
        :param ammo: The Ammo instance.
        :return: None
        """
        v = ammo.velocity
        angle = self._un_convert_angle(angle)

        self.body.apply_impulse_at_local_point((v * cos(radians(angle)), -v * sin(radians(angle))))

    @staticmethod
    def _un_convert_angle(angle):
        """
        Unconverts the arm angle back to a modified coordinate system angle
        (0deg pointing down).

        :param angle: The arm angle in degrees.
        :return: The unconverted angle in degrees.
        """
        # arm deg is already converted,
        # so we need to un-convert it
        angle = (angle - 90) % 360
        return angle
