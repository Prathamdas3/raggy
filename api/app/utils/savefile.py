"""File saving utilities.

Provides functions for securely saving uploaded files to disk.
"""

from app.core.logger import get_logger
from fastapi import UploadFile, File
from uuid import uuid4
from pathlib import Path
from datetime import datetime
from app.core.config import config
import shutil
import re


logger = get_logger()


def save_file(file_type: str, file: UploadFile = File(...)) -> Path:
    """Save an uploaded file to the temp directory.

    Creates a unique filename with timestamp and UUID to prevent collisions,
    and sanitizes the original filename.

    Args:
        file_type: Type/category of the file (e.g., 'document', 'image').
        file: FastAPI UploadFile object.

    Returns:
        Path to the saved file.

    Raises:
        ValueError: If file_type or filename is invalid.
        RuntimeError: If file saving fails.
    """
    logger.debug("Saving the file in the temp directory")

    if not file_type and not file_type.strip():
        raise ValueError("No file type provided")

    file_name = file.filename
    if not file_name or not file_name.strip():
        raise ValueError("No file name found")

    temp_file_path_tmp: Path | None = None

    try:
        safe_name = re.sub(r"[^a-zA-Z0-9._-]", "", file_name)
        unique_name = f"{datetime.now().isoformat()}_{uuid4()}_{safe_name}"

        temp_file_path_tmp = config.temp_dir / (unique_name + ".tmp")
        final_file_path = config.temp_dir / unique_name

        with temp_file_path_tmp.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        temp_file_path_tmp.rename(final_file_path)
        return Path(final_file_path)
    except Exception as e:
        logger.error(f"Failed to save file: {str(e)}", exc_info=True)
        if temp_file_path_tmp is not None and temp_file_path_tmp.exists():
            try:
                logger.error(f"Cleaning up temp file {temp_file_path_tmp} due to error")
                temp_file_path_tmp.unlink()
            except Exception as cleanup_error:
                logger.error(f"Failed to cleanup temp file: {cleanup_error}")

        logger.error(f"Error saving file {file_name}: {str(e)}")
        raise RuntimeError(f"Failed to save file: {str(e)}")
