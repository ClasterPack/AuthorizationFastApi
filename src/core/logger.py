import sys

from loguru import logger


def setup_logging():
    logger.remove()

    logger.add(
        "/usr/src/app/logs/booking/log_on_{time:YYYY-MM-DD}.log",
        rotation="10 MB",
        retention="30 days",
        compression="zip",
        encoding="utf-8",
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
    )
    logger.add(
        sys.stderr,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}"
        "</level> | {name}:{function}:{line} | <cyan>{message}</cyan>",
        level="INFO",
        colorize=True,
    )