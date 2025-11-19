from app.utils.logger import get_logger
from pathlib import Path
from uuid import uuid4
import subprocess

logger = get_logger(__name__)


def compress_video(file_path: Path) -> Path:

    if not file_path:
        raise ValueError("Empty file path provided")
    
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"File does not exist: {file_path}")
    
    if not file_path.is_file():
        raise IsADirectoryError(f"Path is not a file: {file_path}")
    
    # Define compressed file path BEFORE try block to ensure it's in scope
    compressed_name = f"{file_path.stem}_compressed_{uuid4()}.mp4"
    compressed_file_path = file_path.parent / compressed_name
    
    try:
        command = [
            "ffmpeg",
            "-i",
            str(file_path),  # Input file
            "-c:v",
            "libx264",  # Video codec: H.264
            "-preset",
            "medium",  # Compression preset (fast, medium, slow)
            "-crf",
            "28",  # Quality (0-51, lower=better, 28=default)
            "-c:a",
            "aac",  # Audio codec: AAC
            "-b:a",
            "128k",  # Audio bitrate (good quality)
            "-movflags",
            "+faststart",  # Optimize for streaming
            "-y",  # Overwrite output file
            str(compressed_file_path),  # Output file
        ]
        
        logger.info(f"Starting video compression: {file_path} -> {compressed_file_path}")
        
        # Run FFmpeg
        process = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=3600,  # 1 hour timeout
        )
        
        if process.returncode != 0:
            logger.error(f"FFmpeg error: {process.stderr}")
            raise Exception(f"FFmpeg compression failed: {process.stderr}")
        
        logger.info(f"Video compression completed successfully: {compressed_file_path}")
        
    except subprocess.TimeoutExpired:
        logger.error("FFmpeg compression timed out (1 hour limit)")
        # Clean up partial file if it exists
        if compressed_file_path.exists():
            try:
                compressed_file_path.unlink()
                logger.debug(f"Cleaned up timed-out file: {compressed_file_path}")
            except Exception as cleanup_e:
                logger.error(f"Failed to cleanup timed-out file: {str(cleanup_e)}")
        raise Exception("Video compression timed out - file may be too large")
    
    except Exception as e:
        logger.error(f"FFmpeg compression error: {str(e)}")
        # Clean up compressed file if compression failed
        if compressed_file_path.exists():
            try:
                compressed_file_path.unlink()
                logger.debug(f"Cleaned up failed compressed file: {compressed_file_path}")
            except Exception as cleanup_e:
                logger.error(f"Failed to cleanup compressed file: {str(cleanup_e)}")
        raise
    
    # Verify the compressed file is valid
    if not compressed_file_path.exists():
        raise ValueError("Compression failed - output file was not created")
    
    if compressed_file_path.stat().st_size == 0:
        try:
            compressed_file_path.unlink()
            logger.debug(f"Cleaned up empty compressed file: {compressed_file_path}")
        except Exception as e:
            logger.error(f"Failed to cleanup empty compressed file: {str(e)}")
        raise ValueError("Compression failed - resulted in empty data")
    
    return str(compressed_file_path)