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