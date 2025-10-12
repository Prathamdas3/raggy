import asyncio
import shutil
import re
from pathlib import Path
from datetime import datetime, timedelta
from uuid import uuid4
from fastapi import UploadFile, File, HTTPException
from utils.logger import get_logger
from constants import (
    ALLOWED_AUDIO_TYPES,
    ALLOWED_DOC_TYPES,
    ALLOWED_IMAGE_TYPES,
    ALLOWED_VIDEO_TYPES,
)
import magic

logger = get_logger("utils/save_temp_file")

TEMP_DIR = Path("temp")
TEMP_DIR.mkdir(exist_ok=True)
CLEANUP_INTERVAL = 60 * 60  # every 1 hour
FILE_TTL = timedelta(hours=1)  # delete files older than 1 hour


async def detect_file_type(file: UploadFile = File(...)):
    mime_type = magic.from_buffer(await file.read(2048), mime=True)
    await file.seek(0)

    if mime_type in ALLOWED_IMAGE_TYPES:
        return "image"
    elif mime_type in ALLOWED_AUDIO_TYPES:
        return "audio"
    elif mime_type in ALLOWED_VIDEO_TYPES:
        return "video"
    elif mime_type in ALLOWED_DOC_TYPES:
        return "document"
    else:
        raise HTTPException(
            status_code=400, detail=f"Unsupported file type: {mime_type}"
        )


async def save_temp_file(upload_file: UploadFile = File(...)) -> Path:
    logger.info("Initiating save_temp_file function")
    if not upload_file or not hasattr(upload_file, "filename"):
        logger.error("Invalid upload file provided")
        raise ValueError("Invalid upload file")

    file_name = upload_file.filename
    if not file_name:
        raise ValueError("No filename provided")

    # Safe filename
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
    except Exception as e:
        # Clean up temp file if anything goes wrong
        if temp_file_path_tmp.exists():
            logger.error(f"Cleaning up temp file {temp_file_path_tmp} due to error")
            temp_file_path_tmp.unlink()

        logger.error(f"Error saving file {file_name}: {e}")
        raise RuntimeError(f"Failed to save file: {e}")

    return final_file_path


async def cleanup_temp_files():
    logger.info("Starting cleanup_temp_files task")
    while True:
        try:
            now = datetime.now()
            if not TEMP_DIR.exists() or not TEMP_DIR.is_dir():
                logger.info("Temp directory does not exist or is not a directory")
                await asyncio.sleep(CLEANUP_INTERVAL)
                continue

            for file_path in TEMP_DIR.iterdir():
                try:
                    if file_path.is_file():
                        file_age = now - datetime.fromtimestamp(
                            file_path.stat().st_mtime
                        )
                        if file_age > FILE_TTL:
                            file_path.unlink()
                            logger(f"Deleted old temp file: {file_path.name}")
                except FileNotFoundError:
                    # File may have been deleted between iterdir() and stat()
                    continue
                except PermissionError as e:
                    logger.error(
                        f"Permission error deleting file {file_path.name}: {e}"
                    )
                except Exception as e:
                    logger.error(
                        f"Unexpected error deleting file {file_path.name}: {e}"
                    )

        except Exception as e:
            logger.error(f"Unexpected error in cleanup loop: {e}")

        await asyncio.sleep(CLEANUP_INTERVAL)
