import asyncio
import shutil
import re
from pathlib import Path
from datetime import datetime, timedelta
from uuid import uuid4
from fastapi import UploadFile, File, HTTPException
from utils.extractors.others import extract_text_from_othertypes
from utils.logger import get_logger
from constants import (
    ALLOWED_AUDIO_TYPES,
    ALLOWED_DOC_TYPES,
    ALLOWED_IMAGE_TYPES,
    ALLOWED_VIDEO_TYPES,
)
import magic

logger = get_logger("utils/file")

TEMP_DIR = Path("temp")
TEMP_DIR.mkdir(exist_ok=True)
CLEANUP_INTERVAL = 60 * 60  # every 1 hour
FILE_TTL = timedelta(hours=1)  # delete files older than 1 hour


async def handle_file(file: UploadFile = File(...)):
    """
    Handle file upload: detect type and queue for processing.
    
    Returns:
        dict: Contains filename, file_type, and task_id (for document types)
    """
    try:
        # Read first 2048 bytes to detect MIME type
        file_content = await file.read(2048)
        mime_type = magic.from_buffer(file_content, mime=True)
        await file.seek(0)  # Reset file pointer
        
        logger.info(f"Detected MIME type: {mime_type} for file: {file.filename}")
        
        if mime_type in ALLOWED_IMAGE_TYPES:
            logger.info(f"Image file detected: {file.filename}")
            return {"filename": file.filename, "type": "image", "mime_type": mime_type}
        
        elif mime_type in ALLOWED_AUDIO_TYPES:
            logger.info(f"Audio file detected: {file.filename}")
            return {"filename": file.filename, "type": "audio", "mime_type": mime_type}
        
        elif mime_type in ALLOWED_VIDEO_TYPES:
            logger.info(f"Video file detected: {file.filename}")
            return {"filename": file.filename, "type": "video", "mime_type": mime_type}
        
        elif mime_type in ALLOWED_DOC_TYPES:
            logger.info(f"Document file detected: {file.filename}")
            
            # Save the file first
            file_path = await save_temp_file(file)
            logger.info(f"File saved to: {file_path}")
            
            # Queue for text extraction (non-blocking)
            try:
                task = extract_text_from_othertypes.delay(str(file_path), mime_type)
                logger.info(f"Queued extraction task {task.id} for file: {file.filename}")
                
                return {
                    "filename": file.filename,
                    "type": "document",
                    "mime_type": mime_type,
                    "file_path": str(file_path),
                    "task_id": task.id
                }
            except Exception as e:
                logger.error(f"Failed to queue extraction task for {file.filename}: {str(e)}")
                raise RuntimeError(f"Failed to queue file for processing: {str(e)}")
        
        else:
            logger.warning(f"Unsupported file type: {mime_type} for file: {file.filename}")
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type: {mime_type}"
            )
    
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    
    except Exception as e:
        logger.error(f"Error handling file {file.filename}: {str(e)}")
        raise


async def save_temp_file(upload_file: UploadFile = File(...)) -> Path:
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
        
        return final_file_path
    
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


async def cleanup_temp_files():
    """
    Background task to clean up temporary files older than FILE_TTL.
    Runs every CLEANUP_INTERVAL seconds.
    """
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
                            logger.info(f"Deleted old temp file: {file_path.name}")  # Fixed
                
                except FileNotFoundError:
                    # File may have been deleted between iterdir() and stat()
                    continue
                
                except PermissionError as e:
                    logger.error(
                        f"Permission error deleting file {file_path.name}: {str(e)}"
                    )
                
                except Exception as e:
                    logger.error(
                        f"Unexpected error deleting file {file_path.name}: {str(e)}"
                    )

        except Exception as e:
            logger.error(f"Unexpected error in cleanup loop: {str(e)}")

        await asyncio.sleep(CLEANUP_INTERVAL)