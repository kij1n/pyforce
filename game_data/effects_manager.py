import random
from math import radians, cos, sin

from loguru import logger
from pymunk import Vec2d

from shared import Direction, Effect
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

    def add_particles(self, qty, position: Vec2d, direction: Direction):
        logger.debug(f"Adding {qty} particles at {position}, particle qty: {len(self.particles)}")
        p_settings = self.settings["particles"]
        spawn_offset = p_settings["spawn_offset"]
        speed_min, speed_max = p_settings["speed_range"]
        y_vel_min, y_vel_max = p_settings["y_vel_uniform"]
        size_min, size_max = p_settings["size_range"]
        color = p_settings["color"]
        lifetime = p_settings["lifetime"]
        gravity = self.settings["particles"]["gravity"]

        for i in range(qty):
            # get an angle to randomize particle position
            angle = radians(random.randint(0, 360))
            x = int(spawn_offset * cos(angle))
            y = int(spawn_offset * sin(angle))

            vel = Vec2d(
                random.randint(speed_min, speed_max) * (-1 if direction == Direction.LEFT else 1),
                random.randint(speed_min, speed_max) * random.uniform(y_vel_min, y_vel_max) * 2
            )

            size = random.randint(size_min, size_max)
            p = Particle(
                position + Vec2d(x, y),
                vel, size, color,
                lifetime, gravity
            )
            self.particles.append(p)

    def get_effects(self):
        effects = []
        for p in self.particles:
            effect = Effect(
                pos=p.pos, size=p.size, color=p.color, opacity=p.opacity()
            )
            effects.append(effect)
        return effects
