import pymunk
import pytmx
import os
from loguru import logger

class PhysicsEngine:
    def __init__(self, settings: dict):
        logger.info("Initializing physics engine...")

        self.settings = settings
        self.sim = pymunk.Space()
        self._prepare_space()
        self._set_collision_handlers()

        # stores entity ids touching the ground
        self.entities_touching_ground = []

        self.entities_hit = []  # list to store all entities hit by bullets, emptied after hit is resolved

    def _set_collision_handlers(self):
        self.sim.on_collision(
            self.settings["physics"]['collision_types']['player_feet'],
            self.settings["physics"]['collision_types']['platform'],
            begin=self._entity_touching_ground,
            separate=self._entity_leaving_ground
        )
        self.sim.on_collision(
            self.settings["physics"]['collision_types']['enemy_feet'],
            self.settings["physics"]['collision_types']['platform'],
            begin=self._entity_touching_ground,
            separate=self._entity_leaving_ground
        )
        self.sim.on_collision(
            self.settings['physics']['collision_types']['bullet'],
            self.settings['physics']['collision_types']['enemy'],
            begin=self._hit
        )

    def _hit(self, arbiter, space, data):
        bullet = getattr(arbiter.shapes[0], 'bullet', None)
        entity = getattr(arbiter.shapes[1], 'entity', None)  # a bullet is the first shape in the arbiter

        if entity is not None and bullet is not None:
            self.entities_hit.append((entity, bullet))

        return True

    def _entity_touching_ground(self, arbiter, space, data):
        identifier = getattr(arbiter.shapes[0], 'id', None)  # only feet have an id
        if identifier is None:
            return True

        if identifier not in self.entities_touching_ground:
            self.entities_touching_ground.append(identifier)
        return True

    def _entity_leaving_ground(self, arbiter, space, data):
        identifier = getattr(arbiter.shapes[0], 'id', None)
        if identifier is None:
            return True

        identifier = arbiter.shapes[0].id
        if identifier in self.entities_touching_ground:
            self.entities_touching_ground.remove(identifier)
        return True

    def _prepare_space(self):
        self.sim.gravity = pymunk.Vec2d(0, self.settings["physics"]['gravity'])
        self._add_map()
        self.sim.collision_bias = self.settings["physics"]['collision_bias']
        self.sim.collision_slop = self.settings["physics"]['collision_slop']

        logger.info("Physics engine platform collision shapes added.")

    def _add_map(self):
        object_layer = self._get_object_layer()

        for obj in object_layer:
            if obj.width > 1 and obj.height > 1:
                self._add_collision_obj(obj)

    def _add_collision_obj(self, obj):
        add = self._create_shape_body(obj, self.settings)
        self.sim.add(add[1], add[0])

    def _get_object_layer(self):
        try:
            script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            path = os.path.join(script_dir, self.settings["map"]["map_path"])

            if os.name == "nt":
                path = path.replace("/", "\\")

            object_layer = pytmx.TiledMap(path).get_layer_by_name(self.settings["map"]['object_layer_name'])
            return object_layer
        except FileNotFoundError:
            logger.error(f"Map file not found")
        except Exception as e:
            logger.error(f"Unexpected error loading map: {e}")

    @staticmethod
    def _create_shape_body(obj, settings):
        body = pymunk.Body(body_type=pymunk.Body.STATIC)

        x = obj.x
        y = obj.y

        width = obj.width
        height = obj.height

        h_width = width/2
        h_height = height/2

        body.position = pymunk.Vec2d(
            x + h_width,
            y + h_height
        )

        shape = pymunk.Poly(
            body,
            [
                (-h_width, h_height),
                (-h_width, -h_height),
                (h_width, -h_height),
                (h_width, h_height)
            ],
            radius=settings["physics"]['radius']
        )
        shape.friction = settings["physics"]['friction']
        shape.collision_type = settings["physics"]['collision_types']['platform']
        shape.filter = pymunk.ShapeFilter(
            categories=settings['physics']['collision_categories']['platform'],
            mask=settings['physics']['collision_masks']['platform']
        )
        return [shape, body]