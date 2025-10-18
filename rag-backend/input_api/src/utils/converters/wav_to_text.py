from pathlib import Path
from utils.response import APIError
from lib.logger import get_logger
from lib.whisper import get_whisper_model
from utils.files.delete import delete_file
import asyncio
logger=get_logger("utils/converters/wav_to_text")



async def transcribe_audio(audio_file: str) -> str:
    """
    Transcribe WAV audio file to text using OpenAI Whisper.
    Automatically deletes the audio file after successful transcription.
    
    Args:
        audio_file: Path to the WAV audio file
        
    Returns:
        str: Transcribed text from the audio
        
    Raises:
        APIError: With appropriate status codes for different failure scenarios:
            - 400: Invalid input, file not found
            - 500: Transcription/IO errors
    """
    audio_file_path = Path(audio_file)
    
    logger.info(f"Starting audio transcription: {audio_file_path}")
    
    try:
        # ===== Input Validation =====
        if not audio_file:
            logger.error("Empty audio file path provided")
            raise APIError("Audio file path cannot be empty", status_code=400)
        
        if not audio_file_path.exists():
            logger.error(f"Audio file does not exist: {audio_file_path}")
            raise APIError(f"Audio file not found: {audio_file_path}", status_code=404)
        
        if not audio_file_path.is_file():
            logger.error(f"Path is not a file: {audio_file_path}")
            raise APIError(f"Path is not a valid file: {audio_file_path}", status_code=400)
        
        # Check if it's a WAV file
        if audio_file_path.suffix.lower() != ".wav":
            logger.warning(f"File is not a WAV file: {audio_file_path}")
            logger.info("Attempting transcription anyway...")
        
        # ===== Get Whisper Model Instance =====
        try:
            logger.info("Retrieving Whisper model instance")
            whisper_model = get_whisper_model()  # This loads or returns cached instance
            
            if whisper_model is None:
                logger.error("Whisper model is None")
                raise APIError(
                    "Whisper model is not available",
                    status_code=500,
                    details="Failed to load Whisper model"
                )
            logger.info("Whisper model retrieved successfully")
        except APIError:
            raise
        except Exception as e:
            logger.error(f"Failed to get Whisper model: {str(e)}")
            raise APIError(
                "Failed to initialize Whisper model",
                status_code=500,
                details=str(e)
            )
        
        # ===== Transcribe Audio =====
        try:
            logger.info(f"Starting transcription process for: {audio_file_path}")
            
            # Run transcription in thread to avoid blocking
            transcription_result = await asyncio.to_thread(
                whisper_model.transcribe,
                str(audio_file_path),
                language="en"
            )
            
            if not transcription_result or "text" not in transcription_result:
                logger.error("Invalid transcription result format")
                raise APIError(
                    "Transcription returned invalid result",
                    status_code=500
                )
            
            transcribed_text = transcription_result["text"].strip()
            
            if not transcribed_text:
                logger.warning("Transcription resulted in empty text")
                raise APIError(
                    "No speech detected in audio file",
                    status_code=400
                )
            
            logger.info(f"Transcription successful. Text length: {len(transcribed_text)} characters")
            
        except APIError:
            raise
        except Exception as e:
            logger.error(f"Transcription error: {str(e)}")
            raise APIError(
                "Failed to transcribe audio",
                status_code=500,
                details=str(e)
            )
        
        # ===== Delete Audio File =====
        try:
            logger.info(f"Deleting audio file after transcription: {audio_file_path}")
            await delete_file(str(audio_file_path))
            logger.info(f"Audio file deleted successfully: {audio_file_path}")
        except APIError as de:
            # Log warning but don't fail - transcription succeeded
            logger.warning(f"Failed to delete audio file: {de.message}")
        except Exception as e:
            logger.warning(f"Unexpected error deleting audio file: {str(e)}")
        
        logger.info("Transcription completed successfully")
        return transcribed_text
    
    except APIError:
        raise
    
    except Exception as e:
        logger.exception(f"Unexpected error during transcription: {str(e)}")
        raise APIError(
            "Unexpected error during audio transcription",
            status_code=500,
            details=str(e)
        )
