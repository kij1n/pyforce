import pymunk
import pytmx
import os

class PhysicsEngine:
    def __init__(self, settings: dict):
        self.settings = settings
        self.sim = pymunk.Space()
        self._prepare_space()
        self._set_collision_handlers()

        # stores entity ids touching the ground
        self.entities_touching_ground = []

    def _set_collision_handlers(self):
        self.sim.on_collision(
            self.settings["physics"]['collision_types']['player_feet'],
            self.settings["physics"]['collision_types']['platform'],
            begin=self._entity_touching_ground,
            separate=self._entity_leaving_ground
        )

    def _entity_touching_ground(self, arbiter, space, data):
        identifier = getattr(arbiter.shapes[0], 'id', None)
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

    def _add_map(self):
        object_layer = self._get_object_layer()

        for obj in object_layer:
            if obj.width > 1 and obj.height > 1:
                self._add_collision_obj(obj)

    def _add_collision_obj(self, obj):
        add = self._create_shape_body(obj, self.settings)
        self.sim.add(add[1], add[0])

    def _get_object_layer(self):
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(script_dir, self.settings["map"]["map_path"])

        if os.name == "nt":
            path = path.replace("/", "\\")

        object_layer = pytmx.TiledMap(path).get_layer_by_name(self.settings["map"]['object_layer_name'])
        return object_layer

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