import logging
from logging.handlers import RotatingFileHandler
import sys
import os

level = logging.DEBUG if os.environ.get("ENV") == "dev" else logging.INFO


def get_logger(name: str = __name__) -> logging.Logger:
    logger = logging.getLogger(name)

    if logger.hasHandlers():  # Prevent duplicate handlers
        return logger

    logger.setLevel(level)  # default level

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] [%(name)s]: %(message)s"
    )
    console_handler.setFormatter(console_formatter)

    # Rotating file handler
    file_handler = RotatingFileHandler("app.log", maxBytes=5_000_000, backupCount=5)
    file_handler.setLevel(level)
    file_formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] [%(name)s]: %(message)s"
    )
    file_handler.setFormatter(file_formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger
