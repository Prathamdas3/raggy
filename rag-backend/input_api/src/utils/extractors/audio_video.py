import asyncio
from pathlib import Path
from constants import ALLOWED_AUDIO_TYPES, ALLOWED_VIDEO_TYPES
from utils.response import APIError
from utils.celery import celery
from utils.files.delete import  delete_file
import whisper
from utils.logger import get_logger
from utils.whisper import get_whisper_model
import os
import tempfile
import subprocess

logger=get_logger("utils/extractors/audio_video")
model=whisper.load_model("base")


async def convert_audio_video_to_wav(file_path: str, file_type: str) -> str:
    """
    Convert audio or video files to WAV format using FFmpeg.
    Synchronous version for Celery tasks.
    
    Supports:
    - Audio formats: MP3, WAV, FLAC, OGG, WebM, MP4
    - Video formats: MP4, MOV, MKV, AVI, WebM
    
    Args:
        file_path: Path to the audio or video file
        file_type: MIME type of the file
        
    Returns:
        str: Path to the converted WAV audio file
        
    Raises:
        APIError: With appropriate status codes for different failure scenarios:
            - 400: Invalid input, unsupported format
            - 404: File not found
            - 500: Conversion/IO errors
    """
    file_path = Path(file_path)
    wav_file_path = None
    
    logger.info(f"Starting conversion to WAV using FFmpeg. File: {file_path}, Type: {file_type}")
    
    try:
        # ===== Input Validation =====
        if not file_path:
            logger.error("Empty file path provided")
            raise APIError("File path cannot be empty", status_code=400)
        
        if not file_path.exists():
            logger.error(f"File does not exist: {file_path}")
            raise APIError(f"File not found: {file_path}", status_code=404)
        
        if not file_path.is_file():
            logger.error(f"Path is not a file: {file_path}")
            raise APIError(f"Path is not a valid file: {file_path}", status_code=400)
        
        if not file_type:
            logger.error("File type not provided")
            raise APIError("File type must be specified", status_code=400)
        
        # Check if file type is supported
        if file_type not in (ALLOWED_AUDIO_TYPES | ALLOWED_VIDEO_TYPES):
            logger.error(f"Unsupported file type: {file_type}")
            raise APIError(
                f"Unsupported file type: {file_type}. Supported types: audio and video files",
                status_code=400
            )
        
        logger.info(f"File type is supported: {file_type}")
        
        # ===== Create Temporary WAV File =====
        try:
            temp_file = tempfile.NamedTemporaryFile(
                suffix=".wav",
                delete=False,
                dir="temp"
            )
            wav_file_path = temp_file.name
            temp_file.close()
            logger.info(f"Temporary WAV file path: {wav_file_path}")
        except Exception as e:
            logger.error(f"Failed to create temporary WAV file: {str(e)}")
            raise APIError(
                "Failed to create temporary WAV file",
                status_code=500,
                details=str(e)
            )
        
        # ===== Convert to WAV using FFmpeg =====
        try:
            logger.info(f"Starting FFmpeg conversion: {file_path} -> {wav_file_path}")
            
            # FFmpeg command for audio extraction
            command = [
                "ffmpeg",
                "-i", str(file_path),          # Input file
                "-q:a", "0",                   # Highest audio quality
                "-map", "a",                   # Map audio stream
                "-f", "wav",                   # Output format: WAV
                "-y",                          # Overwrite output file without asking
                wav_file_path                  # Output file
            ]
            
            # Run FFmpeg
            process = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour timeout
            )
            
            if process.returncode != 0:
                logger.error(f"FFmpeg error: {process.stderr}")
                raise Exception(f"FFmpeg conversion failed: {process.stderr}")
            
            logger.info("FFmpeg conversion completed successfully")
        
        except subprocess.TimeoutExpired:
            logger.error("FFmpeg conversion timed out (1 hour limit)")
            raise APIError(
                "Audio conversion timed out - file may be too large",
                status_code=500
            )
        except FileNotFoundError:
            logger.error("FFmpeg not found - please install FFmpeg")
            raise APIError(
                "FFmpeg is not installed on the system",
                status_code=500,
                details="Please install FFmpeg to enable audio conversion"
            )
        except Exception as e:
            logger.error(f"FFmpeg conversion error: {str(e)}")
            
            # Clean up WAV file if conversion failed
            if wav_file_path and os.path.exists(wav_file_path):
                try:
                    os.remove(wav_file_path)
                    logger.info(f"Cleaned up failed WAV file: {wav_file_path}")
                except Exception as cleanup_e:
                    logger.error(f"Failed to cleanup WAV file: {str(cleanup_e)}")
            
            raise APIError(
                "Failed to convert file to WAV format",
                status_code=500,
                details=str(e)
            )
        
        # ===== Verify WAV File =====
        if not os.path.exists(wav_file_path):
            logger.error(f"WAV file was not created: {wav_file_path}")
            raise APIError(
                "WAV file was not created successfully",
                status_code=500
            )
        
        file_size = os.path.getsize(wav_file_path)
        
        if file_size == 0:
            logger.error(f"WAV file is empty: {wav_file_path}")
            try:
                os.remove(wav_file_path)
            except Exception as e:
                logger.error(f"Failed to cleanup empty WAV file: {str(e)}")
            
            raise APIError(
                "WAV file created but is empty",
                status_code=500
            )
        
        logger.info(f"WAV file verified. Size: {file_size / (1024*1024):.2f} MB")
        
        # ===== Delete Original File =====
        try:
            logger.info(f"Deleting original file: {file_path}")
            await delete_file(str(file_path))
            logger.info(f"Original file deleted successfully: {file_path}")
        except APIError as de:
            # Log warning but don't fail - WAV was created successfully
            logger.warning(f"Failed to delete original file: {de.message}")
        except Exception as e:
            logger.warning(f"Unexpected error deleting original file: {str(e)}")
        
        logger.info(f"Conversion completed successfully. Output: {wav_file_path}")
        return wav_file_path
    
    except APIError:
        raise
    
    except Exception as e:
        logger.exception(f"Unexpected error during conversion: {str(e)}")
        
        # Clean up WAV file on unexpected error
        if wav_file_path and os.path.exists(wav_file_path):
            try:
                os.remove(wav_file_path)
                logger.info(f"Cleaned up WAV file after error: {wav_file_path}")
            except Exception as cleanup_e:
                logger.error(f"Failed to cleanup WAV file: {str(cleanup_e)}")
        
        raise APIError(
            "Unexpected error during audio conversion",
            status_code=500,
            details=str(e)
        )



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

@celery.task(bind=True)
async def extract_text_from_wav(self, file_path: str, file_type: str) -> dict:
    """
    Celery task to convert audio/video to WAV and transcribe to text.
    
    Process:
    1. Convert audio/video file to WAV format
    2. Transcribe WAV audio to text using Whisper
    3. Delete intermediate files
    4. Return transcribed text
    
    Args:
        file_path: Path to the audio or video file
        file_type: MIME type of the file
        
    Returns:
        dict: {
            "status": "success"/"error",
            "data": {"transcribed_text": "...", "wav_path": "..."},
            "message": "...",
            "code": 200/400/500
        }
    """
    logger.info(f"Celery task started: extract_text_from_wav")
    logger.info(f"File: {file_path}, Type: {file_type}")
    
    wav_file_path = None
    
    try:
        # ===== Step 1: Convert to WAV =====
        logger.info("Step 1: Converting audio/video to WAV format")
        try:
            wav_file_path = await convert_audio_video_to_wav(file_path, file_type)
            logger.info(f"Conversion successful. WAV path: {wav_file_path}")
        except APIError as ae:
            logger.error(f"WAV conversion failed: {ae.message}")
            return {
                "status": "error",
                "message": f"WAV conversion failed: {ae.message}",
                "code": ae.status_code,
                "data": None
            }
        except Exception as e:
            logger.error(f"Unexpected error during WAV conversion: {str(e)}")
            return {
                "status": "error",
                "message": "Unexpected error during WAV conversion",
                "code": 500,
                "data": None
            }
        
        # ===== Step 2: Transcribe WAV to Text =====
        logger.info("Step 2: Transcribing WAV audio to text")
        try:
            # Run async transcription in sync context
            transcribed_text = asyncio.run(transcribe_audio(wav_file_path))
            logger.info(f"Transcription successful. Text length: {len(transcribed_text)} characters")
        except APIError as ae:
            logger.error(f"Transcription failed: {ae.message}")
            return {
                "status": "error",
                "message": f"Transcription failed: {ae.message}",
                "code": ae.status_code,
                "data": None
            }
        except Exception as e:
            logger.error(f"Unexpected error during transcription: {str(e)}")
            return {
                "status": "error",
                "message": "Unexpected error during transcription",
                "code": 500,
                "data": None
            }
        
        # ===== Step 3: Return Success =====
        logger.info("extract_text_from_wav task completed successfully")
        return {
            "status": "success",
            "message": "Audio extracted and transcribed successfully",
            "code": 200,
            "data": {
                "transcribed_text": transcribed_text,
                "wav_path": wav_file_path,
                "file_type": "audio/wav"
            }
        }
    
    except Exception as e:
        logger.exception(f"Unexpected error in extract_text_from_wav task: {str(e)}")
        return {
            "status": "error",
            "message": "Unexpected error during task execution",
            "code": 500,
            "data": None
        }