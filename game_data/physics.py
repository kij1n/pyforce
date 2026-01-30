"""
This module contains the PhysicsEngine class which manages the physical simulation of the game world.
"""
import pymunk
import pytmx
import os
from loguru import logger
from pymunk import ShapeFilter


class PhysicsEngine:
    """
    The PhysicsEngine class handles the pymunk physics simulation, map collisions, and collision callbacks.

    Attributes:
        settings (dict): Dictionary containing game settings.
        sim (pymunk.Space): The pymunk physics simulation space.
        entities_touching_ground (list[int]): List of entity IDs currently touching a platform.
        entities_hit (list): List of (entity, bullet) tuples representing recent hits.
        entities_to_kill (list): List of entities marked for removal (e.g., from falling into water).
    """

    def __init__(self, settings: dict):
        """
        Initializes the PhysicsEngine, sets up the simulation space and collision handlers.

        :param settings: Dictionary containing game settings.
        :return: None
        """
        logger.info("Initializing physics engine...")

        self.settings = settings
        self.sim = pymunk.Space()
        self._prepare_space()
        self._set_collision_handlers()

        # stores entity ids touching the ground
        self.entities_touching_ground = []

        self.entities_hit = []  # list to store all entities hit by bullets, emptied after hit is resolved
        self.entities_to_kill = []

    def _set_collision_handlers(self):
        """
        Registers collision callback functions for various object types in the physics space.

        :return: None
        """
        self.sim.on_collision(
            self.settings["physics"]["collision_types"]["player_feet"],
            self.settings["physics"]["collision_types"]["platform"],
            begin=self._entity_touching_ground,
            separate=self._entity_leaving_ground,
        )
        self.sim.on_collision(
            self.settings["physics"]["collision_types"]["enemy_feet"],
            self.settings["physics"]["collision_types"]["platform"],
            begin=self._entity_touching_ground,
            separate=self._entity_leaving_ground,
        )
        self.sim.on_collision(
            self.settings["physics"]["collision_types"]["bullet"],
            self.settings["physics"]["collision_types"]["enemy"],
            begin=self._hit,
        )
        self.sim.on_collision(
            self.settings["physics"]["collision_types"]["enemy_feet"],
            self.settings["physics"]["collision_types"]["water"],
            begin=self._add_to_kill_list,
        )
        self.sim.on_collision(
            self.settings["physics"]["collision_types"]["player_feet"],
            self.settings["physics"]["collision_types"]["water"],
            begin=self._add_to_kill_list,
        )
        self.sim.on_collision(
            self.settings["physics"]["collision_types"]["player_feet"],
            self.settings["physics"]["collision_types"]["enemy"],
            begin=self._should_touch_ground,
            separate=self._entity_leaving_ground,
        )

    def _should_touch_ground(self, arbiter, space, data):
        """
        Method to determine if the player standing on an enemy should be treated as touching ground.
        :param arbiter: The pymunk Arbiter instance.
        :param space: The pymunk Space.
        :param data: Arbitrary data passed to the callback.
        """
        normal = arbiter.normal
        if normal.y > 0:  # normal is down (y-axis is inverted)
            self._entity_touching_ground(arbiter, space, data)

    def _add_to_kill_list(self, arbiter, space, data):
        """
        Collision callback: Marks an entity for death when it touches water.

        :param arbiter: The pymunk Arbiter instance.
        :param space: The pymunk Space.
        :param data: Arbitrary data passed to the callback.
        :return: True to allow the collision to be processed.
        """
        entity = getattr(arbiter.shapes[0], "entity", None)
        if entity is not None:
            self.entities_to_kill.append(entity)
            logger.info(f"Entity {entity.name} killed by collision with water.")

        return True

    def _hit(self, arbiter, space, data):
        """
        Collision callback: Records a bullet hitting an entity.

        :param arbiter: The pymunk Arbiter instance.
        :param space: The pymunk Space.
        :param data: Arbitrary data passed to the callback.
        :return: True to allow the collision to be processed.
        """
        bullet = getattr(arbiter.shapes[0], "bullet", None)
        entity = getattr(arbiter.shapes[1], "entity", None)  # a bullet is the first shape in the arbiter

        if entity is not None and bullet is not None:
            self.entities_hit.append((entity, bullet))

        return True

    def _entity_touching_ground(self, arbiter, space, data):
        """
        Collision callback: Records an entity touching a platform.

        :param arbiter: The pymunk Arbiter instance.
        :param space: The pymunk Space.
        :param data: Arbitrary data passed to the callback.
        :return: True to allow the collision to be processed.
        """
        identifier = getattr(arbiter.shapes[0], "id", None)  # only feet have an id
        if identifier is None:
            return True

        if identifier not in self.entities_touching_ground:
            self.entities_touching_ground.append(identifier)
        return True

    def _entity_leaving_ground(self, arbiter, space, data):
        """
        Collision callback: Records an entity leaving a platform.

        :param arbiter: The pymunk Arbiter instance.
        :param space: The pymunk Space.
        :param data: Arbitrary data passed to the callback.
        :return: True to allow the collision to be processed.
        """
        identifier = getattr(arbiter.shapes[0], "id", None)
        if identifier is None:
            return True

        identifier = arbiter.shapes[0].id
        if identifier in self.entities_touching_ground:
            self.entities_touching_ground.remove(identifier)
        return True

    def _prepare_space(self):
        """
        Configures gravity and other global physics parameters.

        :return: None
        """
        self.sim.gravity = pymunk.Vec2d(0, self.settings["physics"]["gravity"])
        self._add_map()
        self.sim.collision_bias = self.settings["physics"]["collision_bias"]
        self.sim.collision_slop = self.settings["physics"]["collision_slop"]

        logger.info("Physics engine platform collision shapes added.")

    def _add_map(self):
        """
        Loads map collision objects from the TMX file.

        :return: None
        """
        object_layer = self._get_object_layer()

        for obj in object_layer:
            if obj.width > 1 and obj.height > 1:
                self._add_collision_obj(obj)

        walls = self.settings["physics"]["walls"]
        radius = walls["radius"]
        friction = walls["friction"]
        elasticity = walls["elasticity"]

        for wall in walls["coordinates"]:
            a, b = wall
            segment = pymunk.Segment(self.sim.static_body, (a[0], a[1]), (b[0], b[1]), radius)
            segment.friction = friction
            segment.elasticity = elasticity
            self.sim.add(segment)


    def _add_collision_obj(self, obj):
        """
        Creates and adds a single collision shape to the simulation.

        :param obj: The Tiled map object.
        :return: None
        """
        add = self._create_shape_body(obj, self.settings)
        self.sim.add(add[1], add[0])

    def _get_object_layer(self):
        """
        Retrieves the TMX object layer containing collision data.

        :return: A pytmx.TiledObjectGroup instance.
        """
        try:
            script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            path = os.path.join(script_dir, self.settings["map"]["map_path"])

            if os.name == "nt":
                path = path.replace("/", "\\")

            object_layer = pytmx.TiledMap(path).get_layer_by_name(self.settings["map"]["object_layer_name"])
            return object_layer
        except FileNotFoundError:
            logger.error(f"Map file not found")
        except Exception as e:
            logger.error(f"Unexpected error loading map: {e}")

    @staticmethod
    def _create_shape_body(obj, settings):
        """
        Creates a static physics shape and body for a map object.

        :param obj: The Tiled map object.
        :param settings: Dictionary containing game settings.
        :return: A list [shape, body].
        """
        body = pymunk.Body(body_type=pymunk.Body.STATIC)

        h_width = obj.width / 2
        h_height = obj.height / 2

        body.position = pymunk.Vec2d(obj.x + h_width, obj.y + h_height)

        shape = pymunk.Poly(
            body,
            [(-h_width, h_height), (-h_width, -h_height), (h_width, -h_height), (h_width, h_height)],
            radius=settings["physics"]["radius"],
        )
        shape.friction = settings["physics"]["friction"]

        if obj.type == "water":
            shape.collision_type = settings["physics"]["collision_types"]["water"]
        else:
            shape.collision_type = settings["physics"]["collision_types"]["platform"]

        shape.filter = pymunk.ShapeFilter(
            categories=settings["physics"]["collision_categories"]["platform"],
            mask=settings["physics"]["collision_masks"]["platform"],
        )

        if obj.type == "explosive":  # override settings for explosive objects
            shape.collision_type = settings["physics"]["collision_types"]["explosive"]
            shape.filter = ShapeFilter(
                categories=settings["physics"]["collision_categories"]["explosive"],
                mask=settings["physics"]["collision_masks"]["explosive"],
            )

        return [shape, body]
