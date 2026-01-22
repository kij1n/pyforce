"""
This module contains the JSONManager class which handles loading and saving settings in JSON format.
"""
import json
from loguru import logger


class JSONManager:
    """
    The JSONManager class handles the loading and saving of game settings from/to a JSON file.

    Attributes:
        path (str): The file path to the settings JSON file.
        settings (dict): A dictionary storing the game settings.
    """

    def __init__(self):
        """
        Initializes the JSONManager, sets the default path, and loads settings.

        :return: None
        """
        logger.info("Initializing JSON manager...")

        self.path = "settings.json"
        self.settings = {}
        self.load()

    def __del__(self):
        """
        Ensures settings are saved when the JSONManager instance is destroyed.

        :return: None
        """
        self.save()

    def load(self):
        """
        Loads settings from the JSON file specified by self.path.

        :return: None
        """
        try:
            with open(self.path, "r") as f:
                self.settings = json.load(f)
                logger.info(f"Settings successfully loaded from {self.path}")

        except FileNotFoundError:
            logger.warning("Settings file not found.")
        except json.JSONDecodeError:
            logger.warning("Failed to load settings file, bad JSON format.")
        except Exception as e:
            logger.error(f"Failed to load settings file: {e}")

    def save(self):
        """
        Saves the current settings to the JSON file specified by self.path.

        :return: None
        """
        if (
            len(self.settings.items()) == 0
        ):  # in case of failed loading, don't overwrite existing settings
            return
        try:
            with open(self.path, "w") as f:
                json.dump(self.settings, f, indent=4)
                logger.info(f"Settings saved to {self.path}")

        except FileNotFoundError:
            logger.warning("Settings file not found.")
        except json.JSONDecodeError:
            logger.warning("Failed to load settings file, bad JSON format.")
        except Exception as e:
            logger.error(f"Failed to load settings file: {e}")
