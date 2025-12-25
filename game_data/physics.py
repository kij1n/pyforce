import pymunk


class PhysicsEngine:
    def __init__(self, settings: dict):
        self.settings = settings
        self.sim = pymunk.Space()
        self._prepare_space()

    def _prepare_space(self):
        self.sim.gravity = pymunk.Vec2d(0, self.settings["physics"]['gravity'])
        self._add_map()

    def _add_map(self):
        pass
