import math
from math import cos, sin, radians

import pymunk
from pymunk import Body, Circle, ShapeFilter

from shared import *
from .patrol_path import PatrolPath
from .player import Player
from .enemy import Enemy
from .state_manager import Direction
from .weapon import *

from loguru import logger

class EntityManager:
    def __init__(self, settings: dict):
        logger.info("Initializing entity manager...")

        self.settings = settings
        self.player = Player(settings)
        self.enemies = self._load_enemies()

        logger.info(f"Player and enemies ({len(self.enemies)}) loaded successfully")

        self.weapons = self._load_weapons(self.settings)  # dict name: Weapon
        self.ammo = self._load_ammo(self.settings)  # dict name: Ammo

        logger.info(f"Weapons ({len(self.weapons)}) and ammunition ({len(self.ammo)}) loaded successfully")

        self.bullets_dict = {}  # dict Bullet: Shape
        self.patrol_paths = self._load_patrol_paths()  # list of PatrolPaths

        logger.info(f"Patrol paths ({len(self.patrol_paths)}) loaded successfully")

    def _load_patrol_paths(self)\
            -> list[PatrolPath]:
        patrol_paths = []
        for path in self.settings['patrol_paths']:
            patrol_path = PatrolPath(path['x_range'], path['height'])
            patrol_paths.append(patrol_path)

        return patrol_paths

    def _load_enemies(self) -> list[Enemy]:
        enemies = []

        for enemy_type in self.settings['enemy_info'].keys():
            ent_settings = self.settings['enemy_info'][enemy_type]
            for pos in ent_settings['start_positions']:
                pos = (pos[0], pos[1])
                enemy = Enemy(
                    name=get_enemy_name(enemy_type),
                    skin_color=SkinColor.GROUND,  # to me implemented later, or not
                    settings=self.settings,
                    pos=pos,
                    ent_id=len(enemies) + 2  # player's id is 1
                )
                enemies.append(enemy)

        return enemies

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
        # mouse pos is in relative coordinates,
        # so we need to use the player's rel not abs position
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

        for bullet, shape in self.bullets_dict.items():
            bullet.timer += 1

    def update_entity_states(self):
        for entity in self.get_entities():
            if entity.name == 'player' and self._is_to_idle(entity):
                self._change_state(entity, 'idle')
            # new_state = self._is_proper_state(entity)
            # if new_state is not None:
            #     self._change_state(entity, new_state)

    def _is_proper_state(self, entity):
        # helper function dedicated to enemies
        # possible enemy state: run, idle, attack, death
        pass

    @staticmethod
    def _is_to_idle(entity):
        # helper function dedicated to player
        return (
            entity.shape.body.velocity == (0, 0) and
            entity.state_manager.state.is_on_ground and
            not entity.state_manager.state.get_state() == "idle"
        )

    @staticmethod
    def _change_state(entity, new_state: str):
        entity.state_manager.state.change_state(
            new_state,
            entity.get_position(),
            entity.shape.body
        )

    def update_enemy_action(self, sim):
        # actions to handle: run(to player, patrol), attack
        for enemy in self.enemies:
            self._update_single_enemy(enemy, sim)
            self._apply_enemy_action(enemy)

    def _update_single_enemy(self, enemy: Enemy, sim: pymunk.Space):
        # change enemy's action in accordance to rules
        # 1. check for aggro
        # 2. check for a patrol path
        # 3. else idle
        if self._check_for_aggro(enemy, sim):
            enemy.change_action(EnemyAction.AGGRO) # apply aggro and return
        elif enemy.update_patrol_state(self.patrol_paths):
            # returns false if an enemy is not on a path
            enemy.change_action(EnemyAction.PATROL)
        else:
            enemy.change_action(EnemyAction.IDLE)

    def _check_for_aggro(self, enemy, sim):
        mask = self.settings['physics']['collision_masks']['line_of_sight']
        query_filter = ShapeFilter(
            mask=mask
        )
        radius = self.settings['physics']['segment_query_radius']

        info = sim.segment_query_first(
            enemy.get_position(),
            self.player.get_position(),
            radius=radius,
            shape_filter=query_filter
        )
        shape = info.shape
        if getattr(shape, 'id', None) == self.settings['player_info']['id']\
           and self._in_distance(enemy, shape, self.settings):
            logger.debug('> found aggro')
            return True
        return False

    @staticmethod
    def _in_distance(enemy, shape, settings):
        return (
            enemy.get_position() - shape.body.position
        ).length < settings['enemy_info'][enemy.name.value]['sight']

    def _apply_enemy_action(self, enemy: Enemy):
        current_action = enemy.get_current_action()
        direction = enemy.get_movement_direction()

        # logger.debug(f"action: {current_action}, direction: {direction}")

        if current_action == EnemyAction.AGGRO:
            direction = self._get_direction_to_player(
                enemy.get_position()[0],
                self.player.get_position()[0]
            )

        elif current_action == EnemyAction.IDLE:
            return

        enemy.state_manager.apply_horizontal_velocity(direction)

    @staticmethod
    def _get_direction_to_player(x, player_x):
        if x > player_x:
            return Direction.LEFT
        else:
            return Direction.RIGHT


    def move_player(self, direction: Direction):
        if direction in [Direction.LEFT, Direction.RIGHT]:
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

        for enemy in self.enemies:
            where.append(enemy.state_manager.get_where(player_pos=self.player.get_position()))

        return where

    def get_entities(self):
        ent_list = [self.player] + self.enemies
        return ent_list

    def update_bullets(self):
        to_be_removed = []

        for bullet, shape in self.bullets_dict.items():
            if bullet.timer >= self.settings['physics']['timeout']['bullet']:
                to_be_removed.append((bullet, shape))
                # print("removing bullet: timer")
            elif (bullet.start_pos - shape.body.position).length >= bullet.reach:
                to_be_removed.append((bullet, shape))
                # print(f"removing bullet: positon: {shape.body.position}")

        for bullet, shape in to_be_removed:
            shape.body.space.remove(shape, shape.body)
            del self.bullets_dict[bullet]

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

    @staticmethod
    def _can_shoot(weapon: Weapon):
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
