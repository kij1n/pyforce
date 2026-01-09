import pymunk
from pymunk import Body, Vec2d, Poly, ShapeFilter


def prepare_collision_box(name, settings):
    if name == "player":
        ent_settings = settings["player_info"]
    else:
        ent_settings = settings["enemy_info"][name]

    mass = ent_settings["mass"]
    moment = ent_settings['moment']

    body = _create_body(mass, moment, ent_settings)
    shape = _create_shape(body, ent_settings, settings, name)
    feet = _create_feet(body, ent_settings, settings, name)

    return body, shape, feet

def _create_body(mass, moment, ent_settings):
    moment = float('inf') if moment is None else moment
    body = Body(mass=mass, moment=moment, body_type=Body.DYNAMIC)
    body.position = Vec2d(
        ent_settings['hitbox'][0],
        ent_settings['hitbox'][1]
    )
    return body

def _create_shape(body, ent_settings, settings, name):
    h_x = ent_settings['hitbox'][0] // 2
    h_y = ent_settings['hitbox'][1] // 2
    feet_y = ent_settings['feet_hitbox'][1]

    vertical_shift = _calc_vertical_shift(h_y, -h_y - feet_y)

    shape = Poly(
        body,
        [
            (-h_x, -h_y - vertical_shift),
            (-h_x, h_y - vertical_shift),
            (h_x, h_y - vertical_shift),
            (h_x, -h_y - vertical_shift)
        ]
    )

    shape.friction = ent_settings["friction"]
    shape.collision_type = settings["physics"]["collision_types"][name]

    shape.filter = ShapeFilter(
        categories=settings["physics"]["collision_categories"][name],
        mask=settings["physics"]["collision_masks"][name]
    )

    return shape

def _create_feet(body, ent_settings, settings, name):
    h_x = ent_settings["hitbox"][0] // 2
    h_y = ent_settings["hitbox"][1] // 2
    feet_y = ent_settings["feet_hitbox"][1]

    vertical_shift = _calc_vertical_shift(
        h_y,
        -h_y - feet_y
    )

    feet = Poly(
        body,
        [
            (-h_x, h_y - vertical_shift),
            (-h_x, h_y + feet_y - vertical_shift),
            (h_x, h_y + feet_y - vertical_shift),
            (h_x, h_y - vertical_shift)
        ]
    )
    feet.friction = ent_settings["feet_friction"]
    feet.collision_type = settings["physics"]["collision_types"]["player_feet"]
    feet.id = ent_settings["id"]

    feet.filter = ShapeFilter(
        categories=settings["physics"]["collision_categories"][str(name) + "_feet"],
        mask=settings["physics"]["collision_masks"][str(name) + "_feet"]
    )

    return feet

def _calc_vertical_shift(a, b):
    # formula: a + x = -(b + x)
    # this equation ensures the center of mass is in (0,0)
    # where <a,b> is the range of y values of the hitbox
    return (a + b) / (-2)