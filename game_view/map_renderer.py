import pytmx
import pyscroll
import os
from loguru import logger


class MapRenderer:
    def __init__(self, size, settings: dict):
        self.map = MapLoader(size, settings)

    def render(self, target, screen):
        self.map.draw(target, screen)


class MapLoader:
    def __init__(self, size: tuple[int, int], settings: dict):
        logger.info("Initializing map loader...")

        self.settings = settings

        try:
            script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            path = os.path.join(script_dir, settings["map"]["map_path"])

            if os.name == "nt":
                path = path.replace("/", "\\")

            tmx_data = pytmx.load_pygame(path)
            map_data = pyscroll.data.TiledMapData(tmx_data)

            self.map_layer = pyscroll.BufferedRenderer(map_data, size)
            self.group = pyscroll.PyscrollGroup(map_layer=self.map_layer)

        except FileNotFoundError:
            logger.error(f"Map file not found")
        except Exception as e:
            logger.error(f"Unexpected error loading map: {e}")

        logger.info("Map loaded successfully.")

    def set_center(self, target):
        target = (
            self.settings["screen"]["size_x"] // 2 if target[0] < self.settings["screen"]["size_x"] // 2 else target[0],
            self.settings["screen"]["size_y"] // 2 if target[1] < self.settings["screen"]["size_y"] // 2 else target[1],
        )
        self.group.center(target)

    def draw(self, target, surface):
        self.set_center(target)
        self.group.draw(surface)
