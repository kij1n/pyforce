from math import cos, radians, sin
from pymunk import Body, Circle, ShapeFilter
from shared import BasicBulletInfo

class Bullet:
    def __init__(self, info: BasicBulletInfo, arm_deg, ammo, settings):
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
        return hash(self.id)

    def __eq__(self, other):
        if not isinstance(other, Bullet):
            return NotImplemented
        return self.id == other.id

    def __del__(self):
        del self

    def _create_body_bullet(self, ammo):
        body = Body(
            mass=ammo.bullet_mass,
            moment=float('inf'),
            body_type=Body.DYNAMIC
        )
        body.position = self.pos
        return body

    def _create_shape_bullet(self, ammo, settings):
        shape = Circle(
            self.body,
            ammo.bullet_radius
        )
        shape.collision_type = settings['physics']['collision_types']['bullet']
        shape.filter = ShapeFilter(
            categories=settings['physics']['collision_categories']['player_bullet'],
            mask=settings['physics']['collision_masks']['player_bullet']
        )
        shape.bullet = self
        return shape

    def _apply_bullet_impulse(self, angle, ammo):
        v = ammo.velocity
        angle = self._un_convert_angle(angle)

        self.body.apply_impulse_at_local_point(
            (v * cos(radians(angle)), -v * sin(radians(angle)))
        )

    @staticmethod
    def _un_convert_angle(angle):
        # arm deg is already converted,
        # so we need to un-convert it
        angle = (angle - 90) % 360
        return angle
