from dataclasses import dataclass

from pymunk import Vec2d


class Weapon:
    def __init__(self, rate_of_fire, reach, ammo):
        self.rate_of_fire = rate_of_fire
        self.reach = reach
        self.ammo = ammo
        self.last_shot = 0  # ticks since last shot

    def can_shoot(self):
        if self.last_shot >= self.rate_of_fire:
            self.last_shot = 0
            return True

        return False

    def append_time(self):
        self.last_shot += 1


class Ammo:
    def __init__(self, velocity, damage, bullet_mass, bullet_radius):
        self.velocity = velocity
        self.damage = damage
        self.bullet_mass = bullet_mass
        self.bullet_radius = bullet_radius


@dataclass
class Bullet:
    id: int
    start_pos: Vec2d
    pos: Vec2d  # in update check whether to remove the bullet because reach
    reach: float
    damage: float
    name: str
    timer: int = 0  # ticks since shot