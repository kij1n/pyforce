import sys
import game_state
import datetime
from loguru import logger


def setup_logging():
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
    game = game_state.Controller()
    game.run()
    logger.info("Game ended")


if __name__ == "__main__":
    setup_logging()
    main()
