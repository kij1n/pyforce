"""
This module contains classes for loading and managing game sprites.
"""

import pygame
import os
from loguru import logger
import re


class SpriteLoader:
    """
    The SpriteLoader class handles the loading and caching of all game sprites, including player and enemy sprites.

    Attributes:
        sprites (dict): A dictionary mapping sprite names to Sprite instances.
    """

    def __init__(self, settings: dict):
        """
        Initializes the SpriteLoader and loads all sprites defined in the settings.

        :param settings: Dictionary containing game settings.
        :return: None
        """
        logger.info("Initializing sprite loader...")

        self.sprites = (
            self.load_player(settings)
            | self.load_enemies(settings)
            | self._load_menu_backgrounds(settings)
            | self._load_pickups(settings)
        )

    def _load_pickups(self, settings: dict):
        pickups = {}
        pickup_info = settings["pickups"]["paths"]
        for path in pickup_info.values():
            try:
                image = pygame.image.load(self._get_path(path)).convert_alpha()
                sprite_name = path.split(".")[0].split("/")[-1]
                pickups[sprite_name] = Sprite(image, None)
            except FileNotFoundError:
                logger.error(f"File not found: {path}")
            except pygame.error:
                logger.error(f"Pygame could not load: {path}")
            except Exception as e:
                logger.error(f"Unexpected error loading {path}: {e}")
        return pickups

    def _load_menu_backgrounds(self, settings: dict):
        backgrounds = {}
        for i in ["map", "menu"]:
            path = self._get_path(settings[i]["background_path"])
            try:
                image = pygame.image.load(path).convert()
                sprite = Sprite(image, None)
                sprite_name = i + "_background"

                backgrounds[sprite_name] = sprite
            except FileNotFoundError:
                logger.error(f"File not found: {settings[i]['background_path']}")
            except pygame.error:
                logger.error(f"Pygame could not load: {settings[i]['background_path']}")
            except Exception as e:
                logger.error(f"Unexpected error loading {settings[i]['background_path']}: {e}")

        logger.info("Backgrounds loading complete")

        return backgrounds

    def load_player(self, settings: dict):
        """
        Loads all sprites related to the player.

        :param settings: Dictionary containing game settings.
        :return: A dictionary of player sprites.
        """
        player = {}
        player_info = settings["player_info"]

        for sprite_type in player_info["sprites_paths"].keys():
            index = 1
            for sprite_info in player_info["sprites_paths"][sprite_type]:
                try:
                    path = self._get_path(sprite_info["path"])
                    offset = sprite_info["offset"]
                    rotation = sprite_info.get("rotation", 0)

                    image = pygame.image.load(path).convert_alpha()
                    image = pygame.transform.rotate(image, rotation)
                    sprite = Sprite(image, offset)

                    if sprite_type == "arm":
                        sprite_name = "player_" + sprite_type
                    elif sprite_type in ["guns", "bullet"]:
                        delimiter = "\\" if os.name == "nt" else "/"
                        sprite_name = path.split(".")[0].split(delimiter)[-1]
                    else:
                        sprite_name = "player_" + sprite_type + str(index)
                        index += 1

                    player[sprite_name] = sprite

                except FileNotFoundError:
                    logger.error(f"File not found: {sprite_info['path']} for player")
                except pygame.error:
                    logger.error(f"Pygame could not load: {sprite_info['path']} for player")
                except Exception as e:
                    logger.error(f"Unexpected error loading {sprite_info} for player: {e}")

        logger.info(f"Player sprites loading complete")
        return player

    def load_enemies(self, settings: dict):
        """
        Loads all sprites related to enemies.

        :param settings: Dictionary containing game settings.
        :return: A dictionary of enemy sprites.
        """
        enemies = {}
        enemy_info = settings["enemy_info"]

        for enemy in enemy_info.keys():
            for sprite_type in enemy_info[enemy]["sprites_paths"].keys():
                for sprite_info in enemy_info[enemy]["sprites_paths"][sprite_type]:
                    try:
                        path = self._get_path(sprite_info["path"])
                        offset = sprite_info["offset"]

                        image = pygame.image.load(path).convert_alpha()
                        sprite = Sprite(image, offset)

                        delimiter = "\\" if os.name == "nt" else "/"
                        sprite_name = enemy + "_" + path.split(".")[0].split(delimiter)[-1]

                        enemies[sprite_name] = sprite

                    except FileNotFoundError:
                        logger.error(f"File not found: {sprite_info['path']} for {enemy}")
                    except pygame.error:
                        logger.error(f"Pygame could not load: {sprite_info['path']} for {enemy}")
                    except Exception as e:
                        logger.error(f"Unexpected error loading {sprite_info['path']} for {enemy}: {e}")

            logger.info(f"{enemy} sprites loading complete")
        return enemies

    def get_sprite(self, sprite_name):
        """
        Retrieves a sprite by its name from the cache.

        :param sprite_name: The name of the sprite to retrieve.
        :return: The Sprite instance corresponding to the given name.
        """
        sprite_found = self.sprites.get(sprite_name, None)

        if sprite_found is None:
            # logger.error(f"Sprite not found: {sprite_name}")
            # fallback to run if sprite not found
            sprite_number = int(re.sub(r"\D", "", sprite_name))
            name = sprite_name.split("_")[0] + "_run" + str(sprite_number)
            return self.sprites[name]
        else:
            return self.sprites[sprite_name]

    @staticmethod
    def _get_path(sprite_location):
        """
        Generates an absolute path for a sprite based on its relative location.

        :param sprite_location: The relative path to the sprite file.
        :return: The absolute path to the sprite file.
        """
        # create an absolute path to the sprite
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(script_dir, sprite_location)

        if os.name == "nt":
            path = path.replace("/", "\\")

        return path


class Sprite(pygame.sprite.Sprite):
    """
    The Sprite class represents a single game sprite with its image and offset.

    Attributes:
        image (pygame.Surface): The pygame Surface containing the sprite's image.
        rect (pygame.Rect): The rectangle defining the sprite's position and size.
        offset (tuple): The offset to apply when rendering the sprite.
    """

    def __init__(self, image: pygame.Surface, offset):
        """
        Initializes the Sprite with an image and an offset.

        :param image: The pygame Surface containing the sprite's image.
        :param offset: The offset to apply when rendering the sprite.
        :return: None
        """
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.offset = offset

    def set_position(self, position):
        """
        Sets the center position of the sprite's rectangle.

        :param position: The new center position for the sprite.
        :return: None
        """
        self.rect.center = position

    def invert_copy(self):
        """
        Creates and returns a horizontally flipped copy of the sprite's image.

        :return: A new horizontally flipped pygame.Surface.
        """
        return pygame.transform.flip(self.image, True, False)

    def rotate_copy(self, degrees):
        """
        Creates and returns a rotated copy of the sprite's image.

        :param degrees: The angle in degrees to rotate the image.
        :return: A new rotated pygame.Surface.
        """
        return pygame.transform.rotate(self.image, degrees)
