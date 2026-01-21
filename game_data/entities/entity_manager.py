from game_data.weaponry import *
from .patrol_path import PatrolPath
from .player import Player
from .enemy import Enemy
import pymunk
from pymunk import ShapeFilter, Vec2d
from shared import *
from math import cos, sin, radians
import math


from loguru import logger


class EntityManager:
    def __init__(self, settings: dict, sim: pymunk.Space):
        logger.info("Initializing entity manager...")

        self.settings = settings
        self.sim = sim
        self.player = Player(settings, self)
        self.enemies = self._load_enemies()

        logger.info(f"Player and enemies ({len(self.enemies)}) loaded successfully")

        self.weapons = self._load_weapons(self.settings)  # dict name: Weapon
        self.ammo = self._load_ammo(self.settings)  # dict name: Ammo

        logger.info(f"Weapons ({len(self.weapons)}) and ammunition ({len(self.ammo)}) loaded successfully")

        self.bullets_dict = {}  # dict Bullet: Shape
        self.patrol_paths = self._load_patrol_paths()  # list of PatrolPaths

        logger.info(f"Patrol paths ({len(self.patrol_paths)}) loaded successfully")

    def _load_patrol_paths(self) -> list[PatrolPath]:
        patrol_paths = []
        for path in self.settings["patrol_paths"]:
            patrol_path = PatrolPath(path["x_range"], path["height"])
            patrol_paths.append(patrol_path)

        return patrol_paths

    def _load_enemies(self) -> set[Enemy]:
        enemies = set()

        for enemy_type in self.settings["enemy_info"].keys():
            ent_settings = self.settings["enemy_info"][enemy_type]
            for pos in ent_settings["start_positions"]:
                pos = (pos[0], pos[1])
                enemy = Enemy(
                    name=get_enemy_name(enemy_type),
                    settings=self.settings,
                    pos=pos,
                    ent_id=len(enemies) + 2,  # player's id is 1
                    entity_manager=self,
                )
                enemies.add(enemy)

        return enemies

    @staticmethod
    def _load_weapons(settings):
        weapons = {}

        for name in settings["weapons"]:
            weapon = Weapon(
                rate_of_fire=settings["weapons"][name]["rate_of_fire"],
                reach=settings["weapons"][name]["reach"],
                ammo=None,
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
                bullet_name=settings["ammo"][name]["bullet_name"],
            )
            ammo[name] = amm
        return ammo

    def update_player_aim(self, mouse_pos):
        # mouse pos is in relative coordinates,
        # so we need to use the player's rel not abs position
        player_pos = self.player.get_relative_pos()

        vector = (mouse_pos[0] - player_pos[0], mouse_pos[1] - player_pos[1])
        angle = math.atan2(-vector[1], vector[0]) * (180 / math.pi)
        angle += 90  # 0 degrees must be pointing down, but Y axis is inverted in pygame
        angle = angle % 360

        self.player.arm_deg = angle

    def update_ground_contact(self, entities_touching_ground: list):
        for entity in self.get_entities():
            identifier = getattr(entity.feet, "id", None)

            if identifier in entities_touching_ground:
                entity.state_manager.state.set_on_ground(True)
            else:
                entity.state_manager.state.set_on_ground(False)

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
            if entity.name == "player" and self._is_to_idle(entity):
                self._change_state(entity, StateName.IDLE)

    @staticmethod
    def _is_to_idle(entity):
        # helper function dedicated to player
        return (
            entity.shape.body.velocity == (0, 0)
            and entity.state_manager.state.is_on_ground
            and not entity.state_manager.state.get_state() in [StateName.IDLE, StateName.DEATH]
        )

    @staticmethod
    def _change_state(entity, new_state: str):
        entity.state_manager.state.change_state(new_state, entity.get_position(), entity.shape.body)

    def update_enemy_action(self, sim):
        for enemy in self.enemies:
            self._update_single_enemy(enemy, sim)
            self._apply_enemy_action(enemy, sim)

    def _update_single_enemy(self, enemy: Enemy, sim: pymunk.Space):
        if enemy.get_state() == StateName.DEATH:
            return
        elif self._check_for_attack(enemy):
            self._resolve_enemy_hits(enemy)
            enemy.change_action(EnemyAction.ATTACK)
        elif self._check_for_aggro(enemy, sim):
            enemy.change_action(EnemyAction.AGGRO)
        elif enemy.update_patrol_state(self.patrol_paths):
            # update patrol state returns false if an enemy is not on a path
            enemy.change_action(EnemyAction.PATROL)
        else:
            enemy.change_action(EnemyAction.IDLE)

    def _resolve_enemy_hits(self, enemy):
        if enemy.has_hit():
            self.player.take_damage(enemy.damage_dealt)

    def _check_for_attack(self, enemy) -> bool:
        if self.player.is_dying():
            return False
        player_pos = self.player.get_position()
        enemy_pos = enemy.get_position()
        attack_dist = self.settings["enemy_info"][enemy.name.value]["attack_distance"]
        return (player_pos - enemy_pos).length <= attack_dist

    def _check_for_aggro(self, enemy, sim):
        if self.player.is_dying():
            return False

        query_filter = self._get_query_filter()

        radius = self.settings["physics"]["segment_query_radius"]
        info = sim.segment_query_first(
            enemy.get_position(), self.player.get_position(), radius=radius, shape_filter=query_filter
        )
        shape = info.shape
        if getattr(shape, "id", None) == self.settings["player_info"]["id"] and self._in_distance(
            enemy, shape, self.settings
        ):
            return True
        return False

    @staticmethod
    def _in_distance(enemy, shape, settings):
        return (enemy.get_position() - shape.body.position).length < settings["enemy_info"][enemy.name.value]["sight"]

    def _apply_enemy_action(self, enemy: Enemy, sim):
        current_action = enemy.get_current_action()
        if current_action in [EnemyAction.DEATH, EnemyAction.IDLE]:
            return

        move_dir = enemy.get_movement_direction()
        if current_action in [EnemyAction.AGGRO, EnemyAction.ATTACK]:
            move_dir = self._get_direction_to_player(enemy.get_position()[0], self.player.get_position()[0])
            self._jump_if_gap(enemy, sim)

        enemy.state_manager.apply_horizontal_velocity(move_dir)

    def _jump_if_gap(self, enemy, sim):
        query_filter = self._get_query_filter()
        radius = self.settings["physics"]["segment_query_radius"]
        for inv in [True, False]:
            # inverted means the point is on the right
            gap_point = self._calc_gap_point(enemy.get_position(), inv)
            info = sim.segment_query_first(enemy.get_position(), gap_point, radius=radius, shape_filter=query_filter)

            jump_dir = Direction.LEFT if inv else Direction.RIGHT
            if info is None and jump_dir == enemy.get_movement_direction():
                enemy.state_manager.apply_vertical_push()

    def _calc_gap_point(self, ent_pos: Vec2d, is_inverted):
        angle = self.settings["physics"]["raycast_options"]["angle"]
        length = self.settings["physics"]["raycast_options"]["length"]

        # Convert angle to radians for trigonometric functions
        # The angle in settings has 0 degrees pointing down
        # We need to convert it to a standard angle where 0 degrees is on the positive x-axis
        rad_angle = radians((angle - 90) % 360)

        offset_x = length * cos(rad_angle)
        offset_y = -length * sin(rad_angle)

        if is_inverted:
            offset_x = -offset_x

        point = ent_pos + Vec2d(offset_x, offset_y)
        return point

    def _get_query_filter(self):
        # used for line of sight queries
        mask = self.settings["physics"]["collision_masks"]["line_of_sight"]
        query_filter = ShapeFilter(mask=mask)
        return query_filter

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
        return pos[0], pos[1]

    def get_where_array(self) -> list[Where]:
        where = [self.player.state_manager.get_where()]

        for enemy in self.enemies:
            where.append(enemy.state_manager.get_where(player_pos=self.player.get_position()))

        return where

    def get_entities(self):
        ent_list = [self.player] + list(self.enemies)
        return ent_list

    def update_bullets(self):
        to_be_removed = []

        for bullet, shape in self.bullets_dict.items():
            if bullet.timer >= self.settings["physics"]["timeout"]["bullet"]:
                to_be_removed.append((bullet, shape))
            elif (bullet.start_pos - shape.body.position).length >= bullet.reach:
                to_be_removed.append((bullet, shape))

        for bullet, shape in to_be_removed:
            self._remove_bullet(bullet, shape.body.space)

    def get_bullet(self):
        if not self.weapons[self.player.gun_held].can_shoot():
            return None, None, None

        weapon = self.weapons[self.player.gun_held]
        ammo = self.ammo[self.player.ammo_used]

        info = self._get_basic_bullet_info(weapon, ammo)

        bullet = Bullet(info=info, arm_deg=self.player.arm_deg, ammo=ammo, settings=self.settings)

        return bullet.body, bullet.shape, bullet

    def _get_basic_bullet_info(self, weapon, ammo):
        info = BasicBulletInfo(
            self._get_next_bullet_id(), self.player.get_gun_position(), weapon.reach, ammo.damage, ammo.bullet_name
        )
        return info

    def handle_kills(self, entities_to_kill: list):
        # used to kill entities that touch water
        ents_to_remove = []
        for ent in entities_to_kill:
            if ent.name == "player" and self._check_debug():
                continue
            if self._kill_entity(ent, self.sim):
                ents_to_remove.append(ent)

        for ent in ents_to_remove:
            entities_to_kill.remove(ent)

    def handle_hits(self, entities_hit: list, sim):
        for entity, bullet in entities_hit:
            if bullet.has_collided:
                continue
            bullet.has_collided = True
            entity.take_damage(bullet.damage)
            self._remove_bullet(bullet, sim)
        self.remove_killed(sim)

    def _remove_bullet(self, bullet, sim):
        shape = self.bullets_dict[bullet]
        sim.remove(shape, shape.body)
        del self.bullets_dict[bullet]
        del bullet
        del shape

    def remove_killed(self, sim: pymunk.Space):
        for entity in self.get_entities():
            if entity.name == "player" and self._check_debug():
                continue
            if entity.health <= 0:
                self._kill_entity(entity, sim)

    def _check_debug(self):
        return self.settings["debug"]["player_immortal"]

    def _kill_entity(self, entity, sim: pymunk.Space):
        if not entity.get_state() == StateName.DEATH:
            entity.change_state(StateName.DEATH)
            if entity.name != "player":
                entity.change_action(EnemyAction.DEATH)
            if entity.health > 0:
                entity.health = 0

        if not entity.is_over_dying():
            return False

        self.enemies.discard(entity)
        # sim.remove(entity.shape, entity.feet, entity.body)
        entity.kill()
        return True

    def _get_next_bullet_id(self):
        return max([bullet.id for bullet in self.bullets_dict.keys()] + [0]) + 1

    def remove_entity(self, entity):
        if None not in [entity.body.space, entity.shape.space, entity.feet.space]:
            self.sim.remove(entity.body, entity.shape, entity.feet)
        if entity.name == "player":
            self.player = None
        else:
            self.enemies.discard(entity)
