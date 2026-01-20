import json
from loguru import logger


class JSONManager:
    def __init__(self):
        logger.info("Initializing JSON manager...")

        self.path = "settings.json"
        self.settings = {}
        self.load()

    def __del__(self):
        self.save()

    def load(self):
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
        if len(self.settings.items()) == 0:  # in case of failed loading, don't overwrite existing settings
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
