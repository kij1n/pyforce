"""
This module contains the Ammo class which defines the properties of different ammunition types.
"""


class Ammo:
    """
    The Ammo class stores data related to bullet physics and behavior.

    Attributes:
        velocity (float): The speed at which the bullet travels.
        damage (int): The amount of damage dealt by the bullet.
        bullet_mass (float): The physical mass of the bullet.
        bullet_radius (float): The radius of the bullet's physical shape.
        bullet_name (str): The name or identifier of the bullet type.
    """

    def __init__(self, velocity, damage, bullet_mass, bullet_radius, bullet_name):
        """
        Initializes the Ammo instance with specified properties.

        :param velocity: The speed of the bullet.
        :param damage: The damage value.
        :param bullet_mass: The mass of the bullet.
        :param bullet_radius: The radius of the bullet.
        :param bullet_name: The name of the bullet type.
        :return: None
        """
        self.velocity = velocity
        self.damage = damage
        self.bullet_mass = bullet_mass
        self.bullet_radius = bullet_radius
        self.bullet_name = bullet_name
