from pathlib import Path
from constants import ALLOWED_AUDIO_TYPES, ALLOWED_VIDEO_TYPES
from utils.response import APIError
from utils.files.delete import  delete_file
from lib.logger import get_logger
import os
import tempfile
import subprocess   

logger=get_logger("utils/converters/audio_video_to_wav")


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
