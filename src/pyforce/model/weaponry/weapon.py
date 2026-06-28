"""
This module contains the Weapon class which manages weapon firing logic and properties.
"""


class Weapon:
    """
    The Weapon class represents a firearm in the game.

    Attributes:
        rate_of_fire (int): The number of ticks required between shots.
        reach (float): The maximum distance bullets from this weapon can travel.
        ammo (Ammo): The type of ammunition used by the weapon.
        last_shot (int): The number of ticks since the last shot was fired.
    """

    def __init__(self, rate_of_fire, reach, ammo, accuracy, multishot):
        """
        Initializes a Weapon instance.

        :param rate_of_fire: Ticks between shots.
        :param reach: Maximum bullet travel distance.
        :param ammo: Ammo instance.
        :return: None
        """
        self.rate_of_fire = rate_of_fire
        self.reach = reach
        self.ammo = ammo
        self.last_shot = 0  # ticks since last shot
        self.accuracy = accuracy
        self.multishot = multishot

    def can_shoot(self):
        """
        Checks if the weapon is ready to fire based on the rate of fire.

        :return: True if the weapon can shoot, False otherwise.
        """
        if self.last_shot >= self.rate_of_fire:
            self.last_shot = 0
            return True
        return False

    def append_time(self):
        """
        Increments the timer since the last shot.

        :return: None
        """
        self.last_shot += 1
