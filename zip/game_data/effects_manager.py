import random
from math import radians, cos, sin

from loguru import logger
from pymunk import Vec2d

from shared import Direction, Effect, EnemyName
from .particle import Particle


class EffectsManager:
    def __init__(self, settings: dict):
        self.settings = settings
        self.particles = []

    def update(self, dt):
        alive_particles = []
        for particle in self.particles:
            particle.update(dt)
            if particle.is_alive():
                alive_particles.append(particle)
        self.particles = alive_particles

    def add_particles(self, qty, position: Vec2d, direction: Direction, enemy: EnemyName | str):
        p_settings = self.settings["particles"]
        spawn_offset = p_settings["spawn_offset"]
        speed_min, speed_max = p_settings["speed_range"]
        y_vel_min, y_vel_max = p_settings["y_vel_uniform"]
        y_vel_multiplier = p_settings["y_vel_multiplier"]
        size_min, size_max = p_settings["size_range"]
        lifetime = p_settings["lifetime"]
        gravity = self.settings["particles"]["gravity"]

        color = None
        name = getattr(enemy, "value", "player")
        if name == "player":
            color = p_settings["color"]["player"]
        elif name == EnemyName.GOBLIN.value:
            color = p_settings["color"]["goblin"]
        elif name == EnemyName.SKELETON.value:
            color = p_settings["color"]["skeleton"]

        for i in range(qty):
            # get an angle to randomize particle position
            angle = radians(random.randint(0, 360))
            x = int(spawn_offset * cos(angle))
            y = int(spawn_offset * sin(angle))

            vel = Vec2d(
                random.randint(speed_min, speed_max) * (-1 if direction == Direction.LEFT else 1),
                random.randint(speed_min, speed_max) * random.uniform(y_vel_min, y_vel_max) * y_vel_multiplier,
            )

            size = random.randint(size_min, size_max)
            p = Particle(position + Vec2d(x, y), vel, size, color, lifetime, gravity)
            self.particles.append(p)

    def get_effects(self):
        effects = []
        for p in self.particles:
            effect = Effect(pos=p.pos, size=p.size, color=p.color, opacity=p.opacity())
            effects.append(effect)
        return effects
