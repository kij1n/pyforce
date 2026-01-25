"""
This module contains the EntityManager class which manages all entities in the game,
including the player, enemies, bullets, and their interactions.
"""
from game_data.weaponry import *
from .patrol_path import PatrolPath
from .player import Player
from .enemy import Enemy
import pymunk
from pymunk import ShapeFilter, Vec2d
from shared import *
from math import cos, sin, radians
import math
import random
import weakref


from loguru import logger


class EntityManager:
    """
    The EntityManager class coordinates the lifecycle and interactions of all game entities.

    Attributes:
        settings (dict): Dictionary containing game settings.
        sim (pymunk.Space): The physics simulation space.
        player (Player): The player entity instance.
        enemies (set[Enemy]): A set of active enemy entities.
        weapons (dict): A mapping of weapon names to Weapon instances.
        ammo (dict): A mapping of ammo names to Ammo instances.
        bullets_dict (dict): A dictionary mapping Bullet instances to their physics shapes.
        patrol_paths (list[PatrolPath]): A list of available patrol paths in the level.
    """

    def __init__(self, settings: dict, sim: pymunk.Space, model):
        """
        Initializes the EntityManager with settings and a physics space.

        :param settings: Dictionary containing game settings.
        :param sim: The pymunk.Space instance for physics simulation.
        :return: None
        """
        logger.info("Initializing entity manager...")

        self.model = weakref.proxy(model)
        self.settings = settings
        self.sim = sim
        self.player = Player(settings, self)
        self.enemies = self._load_enemies()
        self.enemies_killed = 0

        logger.info(f"Player and enemies ({len(self.enemies)}) loaded successfully")

        self.weapons = self._load_weapons(self.settings)  # dict name: Weapon
        self.ammo = self._load_ammo(self.settings)  # dict name: Ammo

        logger.info(f"Weapons ({len(self.weapons)}) and ammunition ({len(self.ammo)}) loaded successfully")

        self.bullets_dict = {}  # dict Bullet: Shape
        self.patrol_paths = self._load_patrol_paths()  # list of PatrolPaths

        logger.info(f"Patrol paths ({len(self.patrol_paths)}) loaded successfully")

    def spawn_random_enemy(self):
        enemy_name = random.choice([EnemyName.GOBLIN, EnemyName.SKELETON])
        pos = self._get_rand_pos()
        enemy = Enemy(
            name=get_enemy_name(enemy_name),
            settings=self.settings,
            pos=pos,
            ent_id=self._get_next_enemy_id(),
            entity_manager=self,
        )
        self.enemies.add(enemy)
        self.sim.add(enemy.shape, enemy.feet, enemy.body)
        logger.info(f"Spawned {enemy_name} at {pos}")

    def _get_next_enemy_id(self):
        return max([ent.ent_id for ent in self.enemies] + [1]) + 1  # player's id is 1


    def _get_rand_pos(self) -> Vec2d:
        path = random.choice(self.patrol_paths)
        x = path.get_random_x()
        y = path.height + self.settings["enemy_spawning"]["y_offset"]
        return Vec2d(x, y)

    def apply_difficulty(self, difficulty):
        settings = self.settings["difficulty_changes"][difficulty.value]
        for ent in self.enemies:
            ent.health = settings[ent.name.value]["health"]
            ent.max_health = settings[ent.name.value]["health"]
            ent.damage_dealt = settings[ent.name.value]["damage"]
            ent.state_manager.movement = settings[ent.name.value]["movement"]

    def _load_patrol_paths(self) -> list[PatrolPath]:
        """
        Loads patrol paths from the settings.

        :return: A list of PatrolPath instances.
        """
        patrol_paths = []
        for path in self.settings["patrol_paths"]:
            patrol_path = PatrolPath(path["x_range"], path["height"], path["offset"])
            patrol_paths.append(patrol_path)

        return patrol_paths

    def _load_enemies(self) -> set[Enemy]:
        """
        Loads enemies from the settings and initializes them.

        :return: A set of Enemy instances.
        """
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
        """
        Loads weapon definitions from settings.

        :param settings: Dictionary containing game settings.
        :return: A dictionary of weapon names to Weapon instances.
        """
        weapons = {}

        for name in settings["weapons"]:
            weapon = Weapon(
                rate_of_fire=settings["weapons"][name]["rate_of_fire"],
                reach=settings["weapons"][name]["reach"],
                ammo=None,
                accuracy=settings["weapons"][name]["accuracy"],
                multishot=settings["weapons"][name]["multishot"]
            )
            weapons[name] = weapon
        return weapons

    @staticmethod
    def _load_ammo(settings):
        """
        Loads ammo definitions from settings.

        :param settings: Dictionary containing game settings.
        :return: A dictionary of ammo names to Ammo instances.
        """
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
        """
        Updates the player's arm angle based on the mouse position.

        :param mouse_pos: The screen-relative mouse position.
        :return: None
        """
        # mouse pos is in relative coordinates,
        # so we need to use the player's rel not abs position
        player_pos = self.player.get_relative_pos()

        vector = (mouse_pos[0] - player_pos[0], mouse_pos[1] - player_pos[1])
        angle = math.atan2(-vector[1], vector[0]) * (180 / math.pi)
        angle += 90  # 0 degrees must be pointing down, but Y axis is inverted in pygame
        angle = angle % 360

        self.player.arm_deg = angle

    def update_ground_contact(self, entities_touching_ground: list):
        """
        Updates the ground contact status for all entities.

        :param entities_touching_ground: A list of physics shape IDs that are currently touching the ground.
        :return: None
        """
        for entity in self.get_entities():
            identifier = getattr(entity.feet, "id", None)

            if identifier in entities_touching_ground:
                entity.state_manager.state.set_on_ground(True)
            else:
                entity.state_manager.state.set_on_ground(False)

    def update_timers(self):
        """
        Increments internal timers for animations, weapon rate-of-fire, and bullet lifespan.

        :return: None
        """
        # for entity animations that rely on time
        for entity in self.get_entities():
            entity.state_manager.state.append_time()

        # for weapons' rate of fire
        for weapon in self.weapons.values():
            weapon.append_time()

        for bullet, shape in self.bullets_dict.items():
            bullet.timer += 1

    def update_entity_states(self):
        """
        Updates the high-level states of entities (e.g., transitioning player to idle).

        :return: None
        """
        for entity in self.get_entities():
            if entity.name == "player" and self._is_to_idle(entity):
                self._change_state(entity, StateName.IDLE)

    @staticmethod
    def _is_to_idle(entity):
        """
        Checks if the entity (specifically player) should transition to the IDLE state.

        :param entity: The entity to check.
        :return: True if the entity should be idle, False otherwise.
        """
        # helper function dedicated to player
        return (
            entity.shape.body.velocity == (0, 0)
            and entity.state_manager.state.is_on_ground
            and not entity.state_manager.state.get_state() in [StateName.IDLE, StateName.DEATH]
        )

    @staticmethod
    def _change_state(entity, new_state: str):
        """
        Transitions an entity to a new animation state.

        :param entity: The entity whose state is changing.
        :param new_state: The new state name.
        :return: None
        """
        entity.state_manager.state.change_state(new_state, entity.get_position(), entity.shape.body)

    def update_enemy_action(self, sim):
        """
        Updates the high-level behavior and actions for all enemies.

        :param sim: The physics simulation space.
        :return: None
        """
        for enemy in self.enemies:
            self._update_single_enemy(enemy, sim)
            self._apply_enemy_action(enemy, sim)

    def _update_single_enemy(self, enemy: Enemy, sim: pymunk.Space):
        """
        Updates the action of a single enemy based on player proximity and patrol paths.

        :param enemy: The enemy entity to update.
        :param sim: The physics simulation space.
        :return: None
        """
        if enemy.get_state() == StateName.DEATH:
            return
        elif self._check_for_attack(enemy):
            enemy.change_action(EnemyAction.ATTACK)
            self._resolve_enemy_hits(enemy)
        elif self._check_for_aggro(enemy, sim):
            enemy.change_action(EnemyAction.AGGRO)
        elif enemy.update_patrol_state(self.patrol_paths):
            # update patrol state returns false if an enemy is not on a path
            enemy.change_action(EnemyAction.PATROL)
        else:
            enemy.change_action(EnemyAction.IDLE)

    def _resolve_enemy_hits(self, enemy):
        """
        Checks if an enemy's attack has connected with the player and applies damage.

        :param enemy: The enemy entity performing the attack.
        :return: None
        """
        if enemy.has_hit():
            self.player.take_damage(enemy.damage_dealt)
            self.model.effects.add_particles(
                self.settings["particles"]["qty"],
                self.player.get_position(),
                self._invert_direction(self._get_direction_to_entity(self.player.get_position()[0], enemy.get_position()[0])),
                "player"
            )

    def _check_for_attack(self, enemy) -> bool:
        """
        Checks if the player is within the enemy's attack range.

        :param enemy: The enemy entity.
        :return: True if the player is in attack range, False otherwise.
        """
        if self.player.is_dying():
            return False
        player_pos = self.player.get_position()
        enemy_pos = enemy.get_position()
        attack_dist = self.settings["enemy_info"][enemy.name.value]["attack_distance"]
        return (
            (player_pos - enemy_pos).length <= attack_dist and
            self._check_for_aggro(enemy, self.sim)
        )

    def _check_for_aggro(self, enemy, sim):
        """
        Performs a line-of-sight check to see if the enemy should become aggressive.

        :param enemy: The enemy entity.
        :param sim: The physics simulation space.
        :return: True if the player is seen, False otherwise.
        """
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
        """
        Checks if the player (represented by shape) is within the enemy's sight range.

        :param enemy: The enemy entity.
        :param shape: The player's physics shape.
        :param settings: Dictionary containing game settings.
        :return: True if within distance, False otherwise.
        """
        return (enemy.get_position() - shape.body.position).length < settings["enemy_info"][enemy.name.value]["sight"]

    def _apply_enemy_action(self, enemy: Enemy, sim):
        """
        Applies physical movement or jumping based on the enemy's current action.

        :param enemy: The enemy entity.
        :param sim: The physics simulation space.
        :return: None
        """
        current_action = enemy.get_current_action()
        if current_action in [EnemyAction.DEATH, EnemyAction.IDLE]:
            return

        move_dir = enemy.get_movement_direction()
        if current_action in [EnemyAction.AGGRO, EnemyAction.ATTACK]:
            move_dir = self._get_direction_to_entity(enemy.get_position()[0], self.player.get_position()[0])
            self._jump_if_gap(enemy, sim)

        enemy.state_manager.apply_horizontal_velocity(move_dir)

    def _jump_if_gap(self, enemy, sim):
        """
        Makes the enemy jump if it detects a gap or obstacle in its movement direction.

        :param enemy: The enemy entity.
        :param sim: The physics simulation space.
        :return: None
        """
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
        """
        Calculates a world point used for gap detection raycasting.

        :param ent_pos: The entity's current position.
        :param is_inverted: Whether checking to the left (True) or right (False).
        :return: A Vec2d representing the target point for the raycast.
        """
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
        """
        Creates a physics query filter for line-of-sight checks.

        :return: A pymunk.ShapeFilter instance.
        """
        # used for line of sight queries
        mask = self.settings["physics"]["collision_masks"]["line_of_sight"]
        query_filter = ShapeFilter(mask=mask)
        return query_filter

    @staticmethod
    def _get_direction_to_entity(x1, x2):
        """
        Determines the horizontal direction from an X coordinate to the player's X coordinate.

        :param x: The source X coordinate.
        :return: The Direction (LEFT or RIGHT).
        """
        if x1 > x2:
            return Direction.LEFT
        else:
            return Direction.RIGHT

    def move_player(self, direction: Direction):
        """
        Initiates player movement or jumping in the specified direction.

        :param direction: The direction of movement.
        :return: None
        """
        if direction in [Direction.LEFT, Direction.RIGHT]:
            self.player.state_manager.apply_horizontal_velocity(direction)
        else:
            self.player.state_manager.apply_vertical_push()

    def get_player_pos(self):
        """
        Retrieves the player's current position as a tuple.

        :return: A tuple (x, y).
        """
        pos = self.player.get_position()
        return pos[0], pos[1]

    def get_where_array(self) -> list[Where]:
        """
        Generates a list of Where objects for all entities, used for rendering.

        :return: A list of Where dataclasses.
        """
        where = [self.player.state_manager.get_where()]

        for enemy in self.enemies:
            where.append(enemy.state_manager.get_where())

        return where

    def get_entities(self):
        """
        Retrieves a list of all active entities (player and enemies).

        :return: A list of Player and Enemy instances.
        """
        ent_list = [self.player] + list(self.enemies)
        return ent_list

    def update_bullets(self):
        """
        Updates active bullets, removing those that have timed out or reached their maximum range.

        :return: None
        """
        to_be_removed = []

        for bullet, shape in self.bullets_dict.items():
            if bullet.timer >= self.settings["physics"]["timeout"]["bullet"]:
                to_be_removed.append((bullet, shape))
            elif (bullet.start_pos - shape.body.position).length >= bullet.reach:
                to_be_removed.append((bullet, shape))
            elif bullet.has_collided:
                to_be_removed.append((bullet, shape))

        for bullet, shape in to_be_removed:
            self._remove_bullet(bullet, shape.body.space)

    def get_bullet(self):
        """
        Creates a new bullet if the player's current weapon is ready to fire.

        :return: A tuple (bullet_body, bullet_shape, bullet_instance) or (None, None, None).
        """
        if not self.weapons[self.player.gun_held].can_shoot():
            return None, None, None

        bullets = []

        weapon = self.weapons[self.player.gun_held]
        ammo = self.ammo[self.player.ammo_used]

        accuracy = weapon.accuracy
        for _ in range(weapon.multishot):
            info = self._get_basic_bullet_info(weapon, ammo)
            max_deviation = (1 - accuracy) * 90  # maximum bullet spread angle from arm deg
            deviation = random.uniform(-max_deviation, max_deviation)
            angle = self.player.arm_deg + deviation
            bullet = Bullet(info=info, arm_deg=angle, ammo=ammo, settings=self.settings)
            bullets.append(bullet)
            self.bullets_dict[bullet] = bullet.shape
        return bullets

    def _get_basic_bullet_info(self, weapon, ammo):
        """
        Prepares basic information for a new bullet.

        :param weapon: The Weapon instance being fired.
        :param ammo: The Ammo instance being used.
        :return: A BasicBulletInfo dataclass.
        """
        info = BasicBulletInfo(
            self._get_next_bullet_id(), self.player.get_gun_position(), weapon.reach, ammo.damage, ammo.bullet_name
        )
        return info

    def handle_kills(self, entities_to_kill: list):
        """
        Processes a list of entities to be killed (e.g., from environmental hazards).

        :param entities_to_kill: A list of entities to remove.
        :return: None
        """
        # used to kill entities that touch water
        ents_to_remove = []
        for ent in entities_to_kill:
            try:
                if ent.name == "player" and self._check_debug():
                    continue
                if self._kill_entity(ent, self.sim):
                    ents_to_remove.append(ent)
            except ReferenceError:
                continue

        for ent in ents_to_remove:
            entities_to_kill.remove(ent)

    def handle_hits(self, entities_hit: list, sim):
        """
        Processes bullet collisions with entities.

        :param entities_hit: A list of (entity, bullet) tuples representing collisions.
        :param sim: The physics simulation space.
        :return: None
        """
        for entity, bullet in entities_hit:
            if bullet.has_collided:
                continue
            bullet.has_collided = True
            entity.take_damage(bullet.damage)
            # self._remove_bullet(bullet, sim)

            self.model.effects.add_particles(
                self.settings["particles"]["qty"],
                entity.get_position(),
                self._invert_direction(self._get_direction_to_entity(entity.get_position()[0], self.player.get_position()[0])),
                entity.name
            )

        self.remove_killed(sim)

    @staticmethod
    def _invert_direction(direction):
        return Direction.LEFT if direction == Direction.RIGHT else Direction.RIGHT

    def _remove_bullet(self, bullet, sim):
        """
        Removes a bullet from the physics simulation and the manager's records.

        :param bullet: The Bullet instance to remove.
        :param sim: The physics simulation space.
        :return: None
        """
        shape = self.bullets_dict.get(bullet, None)

        sim.remove(shape, shape.body)
        self.bullets_dict.pop(bullet)

    def remove_killed(self, sim: pymunk.Space):
        """
        Identifies and processes all entities whose health has reached zero.

        :param sim: The physics simulation space.
        :return: None
        """
        for entity in self.get_entities():
            if entity.name == "player" and self._check_debug():
                continue
            if entity.health <= 0:
                self._kill_entity(entity, sim)

    def _check_debug(self):
        """
        Checks if the player is currently immortal due to debug settings.

        :return: True if the player is immortal, False otherwise.
        """
        return self.settings["debug"]["player_immortal"]

    def _kill_entity(self, entity, sim: pymunk.Space):
        """
        Initiates the death process for an entity.

        :param entity: The entity to kill.
        :param sim: The physics simulation space.
        :return: True if the entity has finished its death process and should be removed, False otherwise.
        """
        if not entity.get_state() == StateName.DEATH:
            entity.change_state(StateName.DEATH)
            if entity.name != "player":
                entity.change_action(EnemyAction.DEATH)
            if entity.health > 0:
                entity.health = 0

        if not entity.is_over_dying():
            return False

        self.enemies.discard(entity)
        entity.kill()
        return True

    def _get_next_bullet_id(self):
        """
        Generates a unique ID for a new bullet.

        :return: A unique integer ID.
        """
        return max([bullet.id for bullet in self.bullets_dict.keys()] + [0]) + 1

    def remove_entity(self, entity):
        """
        Removes an entity's physics components from the simulation and updates entity records.

        :param entity: The entity to remove.
        :return: None
        """
        if None not in [entity.body.space, entity.shape.space, entity.feet.space]:
            self.sim.remove(entity.body, entity.shape, entity.feet)
            if entity.name != "player":
                self.enemies_killed += 1
        if entity.name == "player":
            self.player = None
        else:
            self.enemies.discard(entity)
