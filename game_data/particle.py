from pymunk import Vec2d
from pygame import Rect


class Particle:
    def __init__(self, pos: Vec2d, vel: Vec2d, size, color, lifetime, gravity):
        self.pos = pos
        self.size = size

        self.vel = vel
        self.gravity = Vec2d(0, gravity)

        self.color = color
        self.lifetime = lifetime
        self.age = 0

    def update(self, dt):
        self.age += dt
        self.pos += self.vel * dt + self.gravity * dt * dt / 2

    def is_alive(self):
        return self.age < self.lifetime

    def opacity(self):
        return 1 - self.age / self.lifetime
