"""Logging configuration.

Provides structured logging with console and file handlers,
including date-based rotation.
"""

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
    """Custom handler that rotates on both size and time.

    Rotates log files by size (like RotatingFileHandler) and
    creates new files each day with the date in the filename.
    """

    def __init__(
        self,
        folder: str,
        filename: str,
        max_bytes: int = 5_000_000,
        backup_count: int = 5,
    ):
        """Initialize handler with rotation parameters.

        Args:
            folder: Directory for log files.
            filename: Base filename for logs.
            max_bytes: Maximum file size before rotation.
            backup_count: Number of backup files to keep.
        """
        self.folder = folder
        self.base_filename = filename
        self.current_date = datetime.now().strftime("%Y-%m-%d")
        full_path = os.path.join(
            self.folder, f"{self.current_date}_{self.base_filename}"
        )
        super().__init__(full_path, maxBytes=max_bytes, backupCount=backup_count)

    def emit(self, record: logging.LogRecord):
        """Override emit to check date and rotate if needed.

        Creates a new log file with the current date when the date changes.

        Args:
            record: Log record to emit.
        """
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
    """Get a configured logger instance.

    Creates a logger with both console and file handlers,
    including daily rotation.

    Args:
        name: Logger name (typically __name__).

    Returns:
        Configured Logger instance.
    """
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
