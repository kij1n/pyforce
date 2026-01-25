"""
This module provides utility functions for creating and managing entity physics components.
"""
import weakref

from pymunk import Body, Vec2d, Poly, ShapeFilter
from pygame import Rect


def prepare_collision_box(name, settings, entity, pos=None, ent_id=None):
    """
    Creates and configures the physics components (body, shape, and feet) for an entity.

    :param name: The name/type of the entity.
    :param settings: Dictionary containing game settings.
    :param entity: The entity instance to associate with the physics shapes.
    :param pos: Optional initial position. If None, uses default from settings.
    :param ent_id: Optional unique identifier for the entity.
    :return: A tuple containing (body, shape, feet).
    """
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
    """
    Associates the entity instance with its physics shapes.

    :param shape: The main physics shape.
    :param feet: The feet physics shape.
    :param entity: The entity instance.
    :return: None
    """
    shape.entity = weakref.proxy(entity)
    feet.entity = weakref.proxy(entity)


def _create_body(mass, moment, ent_settings, pos=None):
    """
    Creates a pymunk Body for an entity.

    :param mass: The mass of the body.
    :param moment: The moment of inertia.
    :param ent_settings: Settings for the specific entity type.
    :param pos: Initial position.
    :return: A pymunk.Body instance.
    """
    moment = float("inf") if moment is None else moment
    body = Body(mass=mass, moment=moment, body_type=Body.DYNAMIC)
    if pos is None:  # if position is None it's a player
        body.position = Vec2d(ent_settings["start_pos"][0], ent_settings["start_pos"][1])
    else:
        body.position = Vec2d(pos[0], pos[1])
    return body


def _create_shape(body, ent_settings, settings, name, ent_id):
    """
    Creates the main physics shape (Poly) for an entity.

    :param body: The pymunk Body to attach the shape to.
    :param ent_settings: Settings for the specific entity type.
    :param settings: Dictionary containing game settings.
    :param name: The name/type of the entity.
    :param ent_id: Unique identifier for the entity.
    :return: A pymunk.Poly instance.
    """
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
    """
    Creates the feet physics shape (Poly) for ground collision detection.

    :param body: The pymunk Body to attach the feet to.
    :param ent_settings: Settings for the specific entity type.
    :param settings: Dictionary containing game settings.
    :param name: The name/type of the entity.
    :param ent_id: Unique identifier for the entity.
    :return: A pymunk.Poly instance.
    """
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
    """
    Retrieves the collision type for an entity or its feet from settings.

    :param name: The name/type of the entity.
    :param settings: Dictionary containing game settings.
    :param is_feet: Whether to get the collision type for feet.
    :return: An integer representing the collision type.
    """
    ent = name if name == "player" else "enemy"
    if is_feet:
        ent += "_feet"
    return settings["physics"]["collision_types"][ent]


def _get_collision_filter(name, settings, is_feet=False):
    """
    Retrieves the collision filter for an entity or its feet from settings.

    :param name: The name/type of the entity.
    :param settings: Dictionary containing game settings.
    :param is_feet: Whether to get the collision filter for feet.
    :return: A pymunk.ShapeFilter instance.
    """
    ent = name if name == "player" else "enemy"
    if is_feet:
        ent += "_feet"
    return ShapeFilter(
        categories=settings["physics"]["collision_categories"][ent], mask=settings["physics"]["collision_masks"][ent]
    )


def _calc_vertical_shift(a, b):
    """
    Calculates the vertical shift required to center the physics body.

    :param a: Top Y-coordinate of the hitbox.
    :param b: Bottom Y-coordinate of the feet hitbox.
    :return: The vertical shift value.
    """
    # formula: a + x = -(b + x)
    # this equation ensures the center of mass is in (0,0)
    # where <a,b> is the range of y values of the hitbox
    return (a + b) / (-2)


def get_ent_rect(entity):
    """
    Calculates the bounding rectangle for an entity based on its physics shapes.

    :param entity: The entity instance.
    :return: A pygame.Rect instance.
    """
    shape_bb = entity.shape.bb
    feet_bb = entity.feet.bb
    bb = shape_bb.merge(feet_bb)

    width = bb.right - bb.left
    height = bb.top - bb.bottom

    return Rect(int(bb.left), int(bb.bottom), int(width), int(height))
