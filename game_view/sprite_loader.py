import pygame
import os
from loguru import logger

class SpriteLoader:
    def __init__(self, settings: dict):
        logger.info("Initializing sprite loader...")

        self.sprites = (
                self.load_player(settings) |
                self.load_enemies(settings)
        )

    def load_player(self, settings: dict):
        player = {}
        for sprite_type in settings["player_info"]["sprites_paths"].keys():
            index = 1
            for sprite_location in settings["player_info"]["sprites_paths"][sprite_type]:
                try:
                    path = self._get_path(sprite_location)

                    image = pygame.image.load(path).convert_alpha()
                    sprite = Sprite(image)

                    if sprite_type == "arm":
                        sprite_name = "player_" + sprite_type
                    elif sprite_type in ['guns', 'bullet']:
                        delimiter = '\\' if os.name == "nt" else '/'
                        sprite_name = path.split('.')[0].split(delimiter)[-1]
                    else:
                        sprite_name = "player_" + sprite_type + str(index)
                        index += 1

                    player[sprite_name] = sprite

                except FileNotFoundError:
                    logger.error(f"File not found: {sprite_location} for player")
                except pygame.error:
                    logger.error(f"Pygame could not load: {sprite_location} for player")
                except Exception as e:
                    logger.error(f"Unexpected error loading {sprite_location} for player: {e}")


        logger.info(f"Player sprites loading complete")
        return player

    def load_enemies(self, settings: dict):
        enemies = {}
        enemy_info = settings['enemy_info']

        for enemy in enemy_info.keys():
            for sprite_type in enemy_info[enemy]['sprites_paths'].keys():
                for sprite_location in enemy_info[enemy]['sprites_paths'][sprite_type]:
                    try:
                        path = self._get_path(sprite_location)

                        image = pygame.image.load(path).convert_alpha()
                        sprite = Sprite(image)

                        delimiter = '\\' if os.name == "nt" else '/'
                        sprite_name = enemy + "_" + path.split('.')[0].split(delimiter)[-1]

                        enemies[sprite_name] = sprite

                    except FileNotFoundError:
                        logger.error(f"File not found: {sprite_location} for {enemy}")
                    except pygame.error:
                        logger.error(f"Pygame could not load: {sprite_location} for {enemy}")
                    except Exception as e:
                        logger.error(f"Unexpected error loading {sprite_location} for {enemy}: {e}")

            logger.info(f"{enemy} sprites loading complete")
        return enemies


    def get_sprite(self, sprite_name):
        return self.sprites[sprite_name]

    @staticmethod
    def _get_path(sprite_location):
        # create an absolute path to the sprite
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(script_dir, sprite_location)

        if os.name == "nt":
            path = path.replace("/", "\\")

        return path


class Sprite(pygame.sprite.Sprite):
    def __init__(self, image: pygame.Surface):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()

    def set_position(self, position):
        self.rect.center = position

    def invert_copy(self):
        return pygame.transform.flip(self.image, True, False)

    def rotate_copy(self, degrees):
        return pygame.transform.rotate(self.image, degrees)
