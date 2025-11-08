from pathlib import Path
from typing import Union
from app.utils.logger import get_logger
import os

logger = get_logger(__name__)

def remove_file(file_path: Union[str, Path]) -> None:
    file_path = Path(file_path)

    if not str(file_path).strip():
        logger.error("Empty file path provided")
        raise ValueError("File path cannot be empty")

    # Check if the path exists
    if not file_path.exists():
        logger.warning(f"File does not exist: {file_path}")
        raise FileNotFoundError(f"File does not exist: {file_path}")

    # Check if it's actually a file (not a directory)
    if not file_path.is_file():
        logger.error(f"Path is not a file: {file_path}")
        raise IsADirectoryError(f"Path is a directory, not a file: {file_path}")

    # Check if we have permission to delete
    if not os.access(file_path.parent, os.W_OK):
        logger.error(f"No write permission to delete file: {file_path}")
        raise OSError(
            "No permission to delete file (permission denied)",
        )

    try:
        # Attempt to delete the file
        file_path.unlink()

        logger.info(f"File deleted successfully: {file_path}")

    except PermissionError:
        logger.error(f"No permission to delete file: {file_path}")
        raise PermissionError(f"No permission to delete the following path:{file_path}")

    except Exception:
        logger.error("Failed to clean up the give file path")
        raise
