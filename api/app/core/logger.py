import logging
from logging.handlers import RotatingFileHandler
import sys
import os
from datetime import datetime
from app.core.config import config

LOGS_DIR = "logs"
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)


level = logging.DEBUG if config.debug else logging.INFO


class CombinedRotatingHandler(RotatingFileHandler):
    """Custom handler that rotates on both size and time"""

    def __init__(
        self,
        folder: str,
        filename: str,
        max_bytes: int = 5_000_000,
        backup_count: int = 5,
    ):
        self.folder = folder
        self.base_filename = filename
        self.current_date = datetime.now().strftime("%Y-%m-%d")
        full_path = os.path.join(
            self.folder, f"{self.current_date}_{self.base_filename}"
        )
        super().__init__(full_path, maxBytes=max_bytes, backupCount=backup_count)

    def emit(self, record:logging.LogRecord):
        """Override emit to check date and rotate if needed"""
        new_data = datetime.now().strftime("%Y-%m-%d")

        if new_data != self.current_date:
            self.current_date = new_data
            self.close()

            new_filename = os.path.join(
                self.folder, f"{self.current_date}_{self.base_filename}"
            )

            self.baseFilename = new_filename
            self.stream = self._open()

        super().emit(record)


def get_logger(name: str = __name__) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.hasHandlers():
        return logger

    logger.setLevel(level=level)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level=level)
    console_formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] [%(name)s]: %(message)s"
    )
    console_handler.setFormatter(console_formatter)

    file_handler = CombinedRotatingHandler(
        folder=LOGS_DIR,
        filename="app.log",
        max_bytes=5_000_000,
        backup_count=5,
    )

    file_handler.setLevel(level)
    file_formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] [%(name)s]: %(message)s"
    )
    file_handler.setFormatter(file_formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger
