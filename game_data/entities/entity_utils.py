from pymunk import Body, Vec2d, Poly, ShapeFilter
from pygame import Rect


def prepare_collision_box(name, settings, entity, pos=None, ent_id=None):
    if ent_id is None:  # if id is not given, it's a player
        ent_id = getattr(settings["player_info"], "id", 1)

    if name == "player":
        ent_settings = settings["player_info"]
    else:
        ent_settings = settings["enemy_info"][name]

    mass = ent_settings["mass"]
    moment = ent_settings["moment"]

    body = _create_body(mass, moment, ent_settings, pos)
    shape = _create_shape(body, ent_settings, settings, name, ent_id)
    feet = _create_feet(body, ent_settings, settings, name, ent_id)

    _add_ents_to_shapes(shape, feet, entity)

    return body, shape, feet


def _add_ents_to_shapes(shape, feet, entity):
    shape.entity = entity
    feet.entity = entity


def _create_body(mass, moment, ent_settings, pos=None):
    moment = float("inf") if moment is None else moment
    body = Body(mass=mass, moment=moment, body_type=Body.DYNAMIC)
    if pos is None:  # if position is None it's a player
        body.position = Vec2d(ent_settings["start_pos"][0], ent_settings["start_pos"][1])
    else:
        body.position = Vec2d(pos[0], pos[1])
    return body


def _create_shape(body, ent_settings, settings, name, ent_id):
    h_x = ent_settings["hitbox"][0] // 2
    h_y = ent_settings["hitbox"][1] // 2
    feet_y = ent_settings["feet_hitbox"][1]

    vertical_shift = _calc_vertical_shift(h_y, -h_y - feet_y)

    shape = Poly(
        body,
        [
            (-h_x, -h_y - vertical_shift),
            (-h_x, h_y - vertical_shift),
            (h_x, h_y - vertical_shift),
            (h_x, -h_y - vertical_shift),
        ],
    )

    shape.friction = ent_settings["friction"]
    shape.collision_type = _get_collision_type(name, settings)
    shape.id = ent_id  # used to tell if it's a player or enemy

    shape.filter = _get_collision_filter(name, settings)

    return shape


def _create_feet(body, ent_settings, settings, name, ent_id):
    h_x = ent_settings["hitbox"][0] // 2
    h_y = ent_settings["hitbox"][1] // 2
    feet_y = ent_settings["feet_hitbox"][1]

    vertical_shift = _calc_vertical_shift(h_y, -h_y - feet_y)

    feet = Poly(
        body,
        [
            (-h_x, h_y - vertical_shift),
            (-h_x, h_y + feet_y - vertical_shift),
            (h_x, h_y + feet_y - vertical_shift),
            (h_x, h_y - vertical_shift),
        ],
    )
    feet.friction = ent_settings["feet_friction"]
    feet.collision_type = _get_collision_type(name, settings, True)
    feet.id = ent_id  # used in handling ground collisions
    feet.filter = _get_collision_filter(name, settings, True)

    return feet


def _get_collision_type(name, settings, is_feet=False):
    ent = name if name == "player" else "enemy"
    if is_feet:
        ent += "_feet"
    return settings["physics"]["collision_types"][ent]


def _get_collision_filter(name, settings, is_feet=False):
    ent = name if name == "player" else "enemy"
    if is_feet:
        ent += "_feet"
    return ShapeFilter(
        categories=settings["physics"]["collision_categories"][ent], mask=settings["physics"]["collision_masks"][ent]
    )


def _calc_vertical_shift(a, b):
    # formula: a + x = -(b + x)
    # this equation ensures the center of mass is in (0,0)
    # where <a,b> is the range of y values of the hitbox
    return (a + b) / (-2)


def get_ent_rect(entity):
    shape_bb = entity.shape.bb
    feet_bb = entity.feet.bb
    bb = shape_bb.merge(feet_bb)

    width = bb.right - bb.left
    height = bb.top - bb.bottom

    return Rect(int(bb.left), int(bb.bottom), int(width), int(height))
