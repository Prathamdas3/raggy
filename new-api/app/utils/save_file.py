from app.utils.compress_video import compress_video
from app.utils.logger import get_logger
from fastapi import UploadFile, File
from pathlib import Path
from datetime import datetime
from uuid import uuid4
from app.config import config
import shutil
import re

logger = get_logger(__name__)


def save_file(file_type: str, file: UploadFile = File(...)) -> Path:
    logger.debug("Saving the file in the temp repo")
    if not file or not hasattr(file, "filename"):
        logger.error("Invalid upload file provided")
        raise ValueError("Invalid upload file")

    if not file_type or not isinstance(file_type, str):
        raise TypeError("file_type should be a string type")

    if not file_type.strip():
        raise ValueError("file_type can not be emptyI")

    file_name = file.filename
    if not file_name:
        logger.error("No filename provided")
        raise ValueError("No filename provided")
    try:
        safe_name = re.sub(r"[^a-zA-Z0-9._-]", "", file_name)
        unique_name = f"{datetime.now().isoformat()}_{uuid4()}_{safe_name}"

        temp_file_path_tmp = config.TEMP_DIR / (unique_name + ".tmp")
        final_file_path = config.TEMP_DIR / unique_name

        # Write to temporary file (synchronously)
        with temp_file_path_tmp.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        temp_file_path_tmp.rename(final_file_path)

        if file_type == "video":
            compressed_path = compress_video(final_file_path)
            try:
                final_file_path.unlink()
                logger.debug(f"Original uncompressed video deleted: {final_file_path}")
            except Exception as e:
                logger.warning(f"Failed to delete original video: {str(e)}")

            return Path(compressed_path)

    except Exception as e:
        # Clean up temp file if anything goes wrong
        if temp_file_path_tmp.exists():
            try:
                logger.error(f"Cleaning up temp file {temp_file_path_tmp} due to error")
                temp_file_path_tmp.unlink()
            except Exception as cleanup_error:
                logger.error(f"Failed to cleanup temp file: {cleanup_error}")

        logger.error(f"Error saving file {file_name}: {str(e)}")
        raise RuntimeError(f"Failed to save file: {str(e)}")

    return final_file_path
