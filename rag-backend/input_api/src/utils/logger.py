import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
import sys
import os
from datetime import datetime

# Create logs directory if it doesn't exist
LOGS_DIR = "logs"
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)

level = logging.DEBUG if os.environ.get("ENV") == "dev" else logging.INFO


class CombinedRotatingHandler(RotatingFileHandler):
    """
    Custom handler that rotates on both size and time (daily).
    Creates files like: logs/2024-01-15_app.log, logs/2024-01-15_app.log.1, etc.
    """
    
    def __init__(self, folder, filename, max_bytes=5_000_000, backup_count=5):
        self.folder = folder
        self.base_filename = filename
        self.current_date = datetime.now().strftime("%Y-%m-%d")
        
        # Create the full path with date prefix
        full_filename = os.path.join(
            folder, 
            f"{self.current_date}_{filename}"
        )
        
        super().__init__(
            full_filename,
            maxBytes=max_bytes,
            backupCount=backup_count
        )
    
    def emit(self, record):
        """Override emit to check if date has changed"""
        # Check if we need to rotate to a new day
        new_date = datetime.now().strftime("%Y-%m-%d")
        
        if new_date != self.current_date:
            self.current_date = new_date
            # Close the old handler
            self.close()
            
            # Create new filename with new date
            new_filename = os.path.join(
                self.folder,
                f"{self.current_date}_{self.base_filename}"
            )
            self.baseFilename = new_filename
            
            # Reopen with new filename
            self.stream = self._open()
        
        # Continue with normal emit
        super().emit(record)


def get_logger(name: str = __name__) -> logging.Logger:
    """
    Get a logger with console and file handlers.
    
    File logs are saved to 'logs/' folder with daily rotation.
    Files are named like: logs/2024-01-15_app.log
    When a file reaches 5MB, it creates: logs/2024-01-15_app.log.1
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    if logger.hasHandlers():  # Prevent duplicate handlers
        return logger
    
    logger.setLevel(level)
    
    # ===== Console Handler =====
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] [%(name)s]: %(message)s"
    )
    console_handler.setFormatter(console_formatter)
    
    # ===== File Handler with Daily + Size Rotation =====
    file_handler = CombinedRotatingHandler(
        folder=LOGS_DIR,
        filename="app.log",
        max_bytes=5_000_000,  # 5MB per file
        backup_count=5  # Keep 5 backups per day
    )
    file_handler.setLevel(level)
    file_formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] [%(name)s]: %(message)s"
    )
    file_handler.setFormatter(file_formatter)
    
    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger


# Optional: Add custom log levels
def add_custom_log_level(logger):
    """Add custom 'success' log level"""
    logging.SUCCESS = 25
    logging.addLevelName(logging.SUCCESS, "SUCCESS")
    
    def success(self, message, *args, **kws):
        if self.isEnabledFor(logging.SUCCESS):
            self._log(logging.SUCCESS, message, args, **kws)
    
    logging.Logger.success = success
    return logger