import math
from math import cos, sin, radians

from pymunk import Body, Shape, Circle

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
        self.bullets = []  # list[Bullet]

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
        for entity in self.get_entities():
            entity.state_manager.state.append_time()

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

    def get_bullet(self):
        weapon = self.weapons[self.player.gun_held]
        ammo = self.ammo[self.player.ammo_used]

        body = Body(
            mass=ammo.bullet_mass,
            moment=float('inf'),
            body_type=Body.DYNAMIC
        )

        shape = Circle(body, ammo.bullet_radius)
        shape.collision_type = self.settings['physics']['collision_types']['bullet']

        self._apply_bullet_impulse(shape, self.player.arm_deg, ammo)
        return body, shape

    def _apply_bullet_impulse(self, shape, angle, ammo):
        v = ammo.velocity
        angle = self._convert_angle(angle)

        shape.body.apply_impulse_at_local_point(
            v*cos(radians(angle)),
            v*sin(radians(angle))
        )

    @staticmethod
    def _convert_angle(angle):
        angle = (angle - 90) % 360  # due to rotated axes
        angle = (angle + 180) % 360  # inverted Y axis
        return angle