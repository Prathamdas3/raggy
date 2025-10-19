from utils.response import APIError
from lib.celery import celery
from lib.logger import get_logger
from utils.converters.audio_video_to_wav import convert_audio_video_to_wav
from utils.converters.wav_to_text import transcribe_audio

logger = get_logger("utils/extractors/audio_video")


@celery.task(bind=True)
def extract_text_from_wav(
    self, 
    file_path: str, 
    file_type: str,
    user_id: str = None,
    chat_id: str = None
) -> dict:
    """
    Celery task to convert audio/video to WAV, transcribe to text, and queue for splitting.
    
    Process:
    1. Convert audio/video file to WAV format
    2. Transcribe WAV audio to text using Whisper
    3. Delete intermediate files
    4. Queue extracted text for splitting into chunks
    5. Return transcribed text and split task ID
    
    Args:
        file_path: Path to the audio or video file
        file_type: MIME type of the file
        user_id: Optional user ID for tracking
        chat_id: Optional chat ID for tracking
    
    Returns:
        dict: {
            "status": "success"/"error"/"partial_success",
            "data": {"transcribed_text": "...", "wav_path": "...", "split_task_id": "..."},
            "message": "...",
            "code": 200/400/500/206
        }
    """
    logger.info(f"Celery task started: extract_text_from_wav")
    logger.info(f"File: {file_path}, Type: {file_type}, User: {user_id}, Chat: {chat_id}")
    
    wav_file_path = None
    
    # Set defaults for user_id and chat_id if not provided
    user_id = user_id or "unknown"
    chat_id = chat_id or "unknown"
    
    import asyncio
    
    try:
        # ===== Input Validation =====
        if not file_path:
            logger.error("Empty file path provided")
            return {
                "status": "error",
                "message": "File path cannot be empty",
                "code": 400,
                "data": None,
            }
        
        if not file_type:
            logger.error("File type not provided")
            return {
                "status": "error",
                "message": "File type must be specified",
                "code": 400,
                "data": None,
            }
        
        # ===== Step 1: Convert to WAV =====
        logger.info("Step 1: Converting audio/video to WAV format")
        
        try:
            wav_file_path = asyncio.run(
                convert_audio_video_to_wav(file_path, file_type)
            )
            logger.info(f"Conversion successful. WAV path: {wav_file_path}")
        
        except APIError as ae:
            logger.error(f"WAV conversion failed: {ae.message}")
            return {
                "status": "error",
                "message": f"WAV conversion failed: {ae.message}",
                "code": ae.status_code,
                "data": None,
            }
        
        except Exception as e:
            logger.error(f"Unexpected error during WAV conversion: {str(e)}")
            return {
                "status": "error",
                "message": "Unexpected error during WAV conversion",
                "code": 500,
                "data": None,
            }
        
        # ===== Step 2: Transcribe WAV to Text =====
        logger.info("Step 2: Transcribing WAV audio to text")
        
        try:
            transcribed_text = asyncio.run(transcribe_audio(wav_file_path))
            logger.info(
                f"Transcription successful. Text length: {len(transcribed_text)} characters"
            )
        
        except APIError as ae:
            logger.error(f"Transcription failed: {ae.message}")
            return {
                "status": "error",
                "message": f"Transcription failed: {ae.message}",
                "code": ae.status_code,
                "data": None,
            }
        
        except Exception as e:
            logger.error(f"Unexpected error during transcription: {str(e)}")
            return {
                "status": "error",
                "message": "Unexpected error during transcription",
                "code": 500,
                "data": None,
            }
        
        # Validate transcribed text
        if not transcribed_text or not transcribed_text.strip():
            logger.warning(f"No text transcribed from file: {file_path}")
            return {
                "status": "error",
                "message": "No speech detected in audio",
                "code": 400,
                "data": None,
            }
        
        # ===== Step 3: Queue Text for Splitting =====
        logger.info("Step 3: Queueing text for splitting")
        
        split_task_id = None
        split_error = None
        
        try:
            from workers.text_splitter import split_text_task
            
            split_task = split_text_task.delay(transcribed_text, user_id, chat_id)
            split_task_id = split_task.id
            logger.info(f"Queued split_text_task {split_task_id} for extracted text")
        
        except Exception as se:
            logger.error(f"Failed to queue split_text_task: {str(se)}")
            split_error = str(se)
        
        # ===== Return Response =====
        logger.info("extract_text_from_wav task completed")
        
        if split_task_id:
            logger.info(f"Extraction and splitting successful. Split task ID: {split_task_id}")
            return {
                "status": "success",
                "message": "Audio extracted, transcribed, and queued for splitting successfully",
                "code": 200,
                "data": {
                    "transcribed_text": transcribed_text,
                    "text_length": len(transcribed_text),
                    "wav_path": wav_file_path,
                    "file_type": "audio/wav",
                    "split_task_id": split_task_id,
                },
            }
        else:
            # Transcription succeeded but splitting failed
            logger.warning(f"Transcription succeeded but splitting failed: {split_error}")
            return {
                "status": "partial_success",
                "message": "Audio transcribed successfully but failed to queue for splitting",
                "code": 206,  # 206 Partial Content
                "data": {
                    "transcribed_text": transcribed_text,
                    "text_length": len(transcribed_text),
                    "wav_path": wav_file_path,
                    "file_type": "audio/wav",
                    "split_error": split_error,
                },
            }
    
    except Exception as e:
        logger.exception(f"Unexpected error in extract_text_from_wav task: {str(e)}")
        return {
            "status": "error",
            "message": "Unexpected error during task execution",
            "code": 500,
            "data": None,
        }