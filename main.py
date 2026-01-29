"""
This module is the entry point of the application. It sets up logging and starts the game loop.
"""
import sys
import game_state
import datetime
from loguru import logger


def setup_logging():
    """
    Sets up the logging configuration for the game, including console and file output.

    :return: None
    """
    logger.remove()
    logger.add(
        sys.stderr,
        format="[<red>{time:HH:mm:ss}</red>] | {file} | >> " "<yellow>{level}</yellow>: " "<cyan>{message}</cyan>",
    )
    logger.add(
        f"logs/{datetime.datetime.now().strftime('%Y-%m-%d_session-%H-%M-%S')}.log",
        rotation="10 MB",
        retention="3 days",
        format="[<red>{elapsed}</red>] >> " "<yellow>{level}</yellow>: " "<cyan>{message}</cyan>",
    )


def main():
    """
    The main entry point of the game. Initializes the game controller and starts the game loop.

    :return: None
    """
    game = game_state.Controller()

    while game.run():
        game = game_state.Controller()  # reinitialize controller
        logger.info("Restarting game...")  # run returns true if player wants to restart


    logger.info("Game ended")


if __name__ == "__main__":
    setup_logging()
    main()
