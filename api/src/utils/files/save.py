from uuid import uuid4
import shutil
import re
from pathlib import Path
from datetime import datetime
import asyncio
from fastapi import UploadFile, File
from utils.files.compress import compress_video
from utils.response import APIError
from lib.logger import get_logger
from constants import ALLOWED_VIDEO_TYPES

logger = get_logger("utils/file/save")
TEMP_DIR = Path("temp")
TEMP_DIR.mkdir(exist_ok=True)


async def save_temp_file(
    upload_file: UploadFile = File(...), file_type: str = None
) -> Path:
    """
    Save uploaded file to temporary directory with unique name.

    Args:
        upload_file: The uploaded file from FastAPI

    Returns:
        Path: Full path to the saved file

    Raises:
        ValueError: If upload file is invalid
        RuntimeError: If file save operation fails
    """
    logger.info("Initiating save_temp_file function")

    if not upload_file or not hasattr(upload_file, "filename"):
        logger.error("Invalid upload file provided")
        raise ValueError("Invalid upload file")

    file_name = upload_file.filename
    if not file_name:
        logger.error("No filename provided")
        raise ValueError("No filename provided")

    # Create safe filename
    safe_name = re.sub(r"[^a-zA-Z0-9._-]", "", file_name)
    unique_name = f"{datetime.now().isoformat()}_{uuid4()}_{safe_name}"

    # Temporary file first
    temp_file_path_tmp = TEMP_DIR / (unique_name + ".tmp")
    final_file_path = TEMP_DIR / unique_name

    try:
        logger.info(f"Starting to save file {file_name} to {temp_file_path_tmp}")

        # Write to temporary file
        with temp_file_path_tmp.open("wb") as buffer:
            await asyncio.to_thread(shutil.copyfileobj, upload_file.file, buffer)

        logger.info(f"File {file_name} saved successfully to {temp_file_path_tmp}")

        # Rename to final name only if successful
        logger.info(f"Renaming temp file to final file {final_file_path}")
        temp_file_path_tmp.rename(final_file_path)
        logger.info(f"File {file_name} renamed successfully to {final_file_path}")

        # ===== Compress Video if It's a Video File =====
        if file_type in ALLOWED_VIDEO_TYPES:
            logger.info(f"Video file detected. Starting compression: {final_file_path}")

            try:
                compressed_path = await compress_video(str(final_file_path))

                # Delete original uncompressed video
                try:
                    final_file_path.unlink()
                    logger.info(
                        f"Original uncompressed video deleted: {final_file_path}"
                    )
                except Exception as e:
                    logger.warning(f"Failed to delete original video: {str(e)}")

                return Path(compressed_path)

            except APIError as ae:
                logger.error(f"Video compression failed: {ae.message}")
                # Clean up the uncompressed file
                try:
                    final_file_path.unlink()
                except Exception as e:
                    logger.error(f"Failed to cleanup uncompressed file: {str(e)}")

                raise RuntimeError(f"Video compression failed: {ae.message}")

        return final_file_path

    except RuntimeError:
        raise
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
