from fastapi import UploadFile, File, HTTPException
from utils.files.save import save_temp_file
from utils.extractors.audio_video import extract_text_from_wav
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


async def handle_file(
    chat_id: str,
    user_id: str,
    file: UploadFile = File(...)
) -> dict:
    """
    Handle file upload: detect type, save if needed, and queue for processing.
    
    Process:
    1. Detect MIME type
    2. Validate file type is supported
    3. Save file to temp directory (only if supported)
    4. Queue for appropriate processing based on type
    
    Returns:
        dict: Contains filename, file_type, task_id, and file_path (if saved)
    """
    try:
        # ===== Step 1: Detect MIME Type =====
        logger.info(f"Received file: {file.filename} from user: {user_id}, chat: {chat_id}")
        
        # Read first 2048 bytes to detect MIME type
        file_content = await file.read(2048)
        mime_type = magic.from_buffer(file_content, mime=True)
        await file.seek(0)  # Reset file pointer
        
        logger.info(f"Detected MIME type: {mime_type} for file: {file.filename}")
        
        # ===== Step 2: Validate File Type =====
        is_supported = mime_type in (
            ALLOWED_IMAGE_TYPES 
            | ALLOWED_AUDIO_TYPES 
            | ALLOWED_VIDEO_TYPES 
            | ALLOWED_DOC_TYPES
        )
        
        if not is_supported:
            logger.warning(f"Unsupported file type: {mime_type} for file: {file.filename}")
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {mime_type}"
            )
        
        # ===== Step 3: Save File (only after type verification) =====
        logger.info(f"File type is supported. Saving file: {file.filename}")
        
        try:
            file_path = await save_temp_file(file, mime_type)
            logger.info(f"File saved successfully to: {file_path}")
        except Exception as e:
            logger.error(f"Failed to save file {file.filename}: {str(e)}")
            raise RuntimeError(f"Failed to save file: {str(e)}")
        
        # ===== Step 4: Queue for Processing Based on Type =====
        
        # Image Files
        if mime_type in ALLOWED_IMAGE_TYPES:
            logger.info(f"Image file detected: {file.filename}")
            return {
                "filename": file.filename,
                "type": "image",
                "mime_type": mime_type,
                "file_path": str(file_path),
                "user_id": user_id,
                "chat_id": chat_id
            }
        
        # Audio Files
        elif mime_type in ALLOWED_AUDIO_TYPES:
            logger.info(f"Audio file detected: {file.filename}")
            
            try:
                logger.info(f"Queueing audio transcription task for: {file.filename}")
                task = await extract_text_from_wav.delay(str(file_path), mime_type)
                logger.info(f"Queued transcription task {task.id} for audio file: {file.filename}")
                
                return {
                    "filename": file.filename,
                    "type": "audio",
                    "mime_type": mime_type,
                    "file_path": str(file_path),
                    "task_id": task.id,
                }
            except Exception as e:
                logger.error(f"Failed to queue audio transcription task for {file.filename}: {str(e)}")
                raise RuntimeError(f"Failed to queue audio for processing: {str(e)}")
        
        # Video Files
        elif mime_type in ALLOWED_VIDEO_TYPES:
            logger.info(f"Video file detected: {file.filename}")
            
            try:
                logger.info(f"Queueing video transcription task for: {file.filename}")
                task = await extract_text_from_wav.delay(str(file_path), mime_type)
                logger.info(f"Queued transcription task {task.id} for video file: {file.filename}")
                
                return {
                    "filename": file.filename,
                    "type": "video",
                    "mime_type": mime_type,
                    "file_path": str(file_path),
                    "task_id": task.id,
                }
            except Exception as e:
                logger.error(f"Failed to queue video transcription task for {file.filename}: {str(e)}")
                raise RuntimeError(f"Failed to queue video for processing: {str(e)}")
        
        # Document Files
        elif mime_type in ALLOWED_DOC_TYPES:
            logger.info(f"Document file detected: {file.filename}")
            
            try:
                logger.info(f"Queueing document text extraction task for: {file.filename}")
                task = extract_text_from_othertypes.delay(str(file_path), mime_type)
                logger.info(f"Queued extraction task {task.id} for document file: {file.filename}")
                
                return {
                    "filename": file.filename,
                    "type": "document",
                    "mime_type": mime_type,
                    "file_path": str(file_path),
                    "task_id": task.id,
                }
            except Exception as e:
                logger.error(f"Failed to queue document extraction task for {file.filename}: {str(e)}")
                raise RuntimeError(f"Failed to queue document for processing: {str(e)}")
    
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    
    except RuntimeError:
        raise  # Re-raise RuntimeError
    
    except Exception as e:
        logger.error(f"Unexpected error handling file {file.filename}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Unexpected error processing file"
        )







