from dataclasses import dataclass

from pymunk import Vec2d


class Weapon:
    def __init__(self, rate_of_fire, reach, ammo):
        self.rate_of_fire = rate_of_fire
        self.reach = reach
        self.ammo = ammo


class Ammo:
    def __init__(self, velocity, damage, bullet_mass, bullet_radius):
        self.velocity = velocity
        self.damage = damage
        self.bullet_mass = bullet_mass
        self.bullet_radius = bullet_radius


@dataclass
class Bullet:
    pos: tuple
    velocity: float
    angle: float  # degrees
    reach: float
    damage: float
    mass: float