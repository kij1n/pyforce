import math
from math import cos, sin, radians

from pymunk import Body, Shape, Circle, Vec2d, ShapeFilter

from shared import Where
from .player import Player
from .enemy import Enemy
from .weapon import Weapon
from .weapon import Ammo
from .weapon import Bullet


class EntityManager:
    def __init__(self, settings: dict):
        self.settings = settings
        self.player = Player(settings)
        self.enemies = {
            # 'enemy1': Enemy(settings),
            # 'enemy2': Enemy(settings),
        }
        self.weapons = self._load_weapons(self.settings)  # dict name: Weapon
        self.ammo = self._load_ammo(self.settings)  # dict name: Ammo
        self.bullets_dict = {}  # dict Bullet: Shape

    @staticmethod
    def _load_weapons(settings):
        weapons = {}

        for name in settings["weapons"]:
            weapon = Weapon(
                rate_of_fire=settings["weapons"][name]["rate_of_fire"],
                reach=settings["weapons"][name]["reach"],
                ammo=None
            )
            weapons[name] = weapon
        return weapons

    @staticmethod
    def _load_ammo(settings):
        ammo = {}

        for name in settings["ammo"]:
            amm = Ammo(
                velocity=settings["ammo"][name]["velocity"],
                damage=settings["ammo"][name]["damage"],
                bullet_mass=settings["ammo"][name]["bullet_mass"],
                bullet_radius=settings["ammo"][name]["bullet_radius"],
            )
            ammo[name] = amm
        return ammo

    def update_player_aim(self, mouse_pos):
        # mouse pos is in relative coordinates
        # so we need to use player's rel not abs position
        player_pos = self.player.get_relative_pos()

        vector = (
            mouse_pos[0] - player_pos[0],
            mouse_pos[1] - player_pos[1]
        )
        angle = math.atan2(-vector[1], vector[0]) * (180 / math.pi)
        angle += 90  # 0 degrees must be pointing down, but Y axis is inverted in pygame
        angle = angle % 360

        self.player.arm_deg = angle

    def update_ground_contact(self, entities_touching_ground: list):
        for entity in self.get_entities():
            identifier = getattr(entity.feet, 'id', None)

            if identifier in entities_touching_ground:
                entity.state_manager.state.set_on_ground(True, entity.shape.body)
            else:
                entity.state_manager.state.set_on_ground(False, entity.shape.body)

    def update_timers(self):
        # for entity animations that rely on time
        for entity in self.get_entities():
            entity.state_manager.state.append_time()

        # for weapons' rate of fire
        for weapon in self.weapons.values():
            weapon.append_time()

    def update_entity_states(self):
        for entity in self.get_entities():
            if (entity.shape.body.velocity == (0, 0) and
                    entity.state_manager.state.is_on_ground and
                    not entity.state_manager.state.get_state() == "idle"):
                entity.state_manager.state.change_state("idle", entity.get_position(), entity.shape.body)

    def move_player(self, direction: str):
        if direction in ["left", "right"]:
            self.player.state_manager.apply_horizontal_velocity(direction)
        else:
            self.player.state_manager.apply_vertical_push()

    def get_player_pos(self):
        pos = self.player.get_position()
        return (
            pos[0], pos[1]
        )

    def get_where_array(self) -> list[Where]:
        where = [self.player.state_manager.get_where()]

        for enemy in self.enemies.values():
            where.append(enemy.state_manager.get_where(player_pos=self.player.get_position()))

        return where

    def get_entities(self):
        return [
            self.player,
            # self.enemies.values()
        ]

    def update_bullets(self):
        # for bullet, shape in self.bullets_dict.values():
        #     bullet.pos = shape.body.position
        pass

    def get_bullet(self):
        if not self._can_shoot(self.weapons[self.player.gun_held]):
            return None, None, None

        weapon = self.weapons[self.player.gun_held]
        ammo = self.ammo[self.player.ammo_used]

        body = self._create_body_bullet(ammo, self.player.get_gun_position())
        shape = self._create_shape_bullet(ammo, body, self.settings)
        bullet = self._create_bullet_entity(
            self.player.get_gun_position(),
            ammo, weapon,
            id_counter=len(self.bullets_dict)
        )

        self._apply_bullet_impulse(shape, self.player.arm_deg, ammo)
        return body, shape, bullet

    def _can_shoot(self, weapon: Weapon):
        if weapon.can_shoot():
            return True
        return False

    @staticmethod
    def _create_bullet_entity(start_pos, ammo, weapon, id_counter):
        bullet = Bullet(
            id=id_counter + 1,
            start_pos=start_pos,
            pos=start_pos,
            reach=weapon.reach,
            damage=ammo.damage,
            name='bullet'
        )
        return bullet

    @staticmethod
    def _create_shape_bullet(ammo, body, settings):
        shape = Circle(
            body,
            ammo.bullet_radius
        )
        shape.collision_type = settings['physics']['collision_types']['bullet']
        shape.filter = ShapeFilter(
            categories=settings['physics']['collision_categories']['player_bullet'],
            mask=settings['physics']['collision_masks']['player_bullet']
        )
        return shape

    @staticmethod
    def _create_body_bullet(ammo, pos: Vec2d):
        body = Body(
            mass=ammo.bullet_mass,
            moment=float('inf'),
            body_type=Body.DYNAMIC
        )
        body.position = pos
        return body

    def _apply_bullet_impulse(self, shape, angle, ammo):
        v = ammo.velocity
        angle = self._convert_angle(angle)

        shape.body.apply_impulse_at_local_point(
            (v * cos(radians(angle)), -v * sin(radians(angle)))
        )

    @staticmethod
    def _convert_angle(angle):
        # arm deg is already converted
        # so we need to un-convert it
        angle = (angle - 90) % 360
        return angle
