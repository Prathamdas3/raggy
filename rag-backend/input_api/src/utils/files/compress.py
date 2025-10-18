from pathlib import Path
from utils.response import APIError
from lib.logger import get_logger
import asyncio
import subprocess
from uuid import uuid4

logger = get_logger("utils/files/compress")


async def compress_video(file_path: str) -> str:
    """
    Compress video file while preserving audio quality.
    Uses H.264 codec with optimized settings for file size reduction.
    
    Args:
        file_path: Path to the video file to compress
        
    Returns:
        str: Path to the compressed video file
        
    Raises:
        APIError: With appropriate status codes for different failure scenarios
    """
    file_path = Path(file_path)
    compressed_file_path = None
    
    logger.info(f"Starting video compression: {file_path}")
    
    try:
        # ===== Input Validation =====
        if not file_path:
            logger.error("Empty file path provided")
            raise APIError("File path cannot be empty", status_code=400)
        
        if not file_path.exists():
            logger.error(f"Video file does not exist: {file_path}")
            raise APIError(f"Video file not found: {file_path}", status_code=404)
        
        if not file_path.is_file():
            logger.error(f"Path is not a file: {file_path}")
            raise APIError(f"Path is not a valid file: {file_path}", status_code=400)
        
        # Get original file size
        original_size = file_path.stat().st_size
        logger.info(f"Original file size: {original_size / (1024*1024):.2f} MB")
        
        # ===== Create Compressed File Path =====
        compressed_name = f"{file_path.stem}_compressed_{uuid4()}.mp4"
        compressed_file_path = file_path.parent / compressed_name
        logger.info(f"Compressed file will be saved to: {compressed_file_path}")
        
        # ===== Compress Video =====
        try:
            logger.info("Starting FFmpeg compression process")
            
            # FFmpeg command for H.264 compression with audio preservation
            command = [
                "ffmpeg",
                "-i", str(file_path),           # Input file
                "-c:v", "libx264",              # Video codec: H.264
                "-preset", "medium",             # Compression preset (fast, medium, slow)
                "-crf", "28",                   # Quality (0-51, lower=better, 28=default)
                "-c:a", "aac",                  # Audio codec: AAC
                "-b:a", "128k",                 # Audio bitrate (good quality)
                "-movflags", "+faststart",      # Optimize for streaming
                "-y",                           # Overwrite output file
                str(compressed_file_path)       # Output file
            ]
            
            # Run FFmpeg
            process = await asyncio.to_thread(
                subprocess.run,
                command,
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour timeout
            )
            
            if process.returncode != 0:
                logger.error(f"FFmpeg error: {process.stderr}")
                raise Exception(f"FFmpeg compression failed: {process.stderr}")
            
            logger.info("FFmpeg compression process completed")
        
        except subprocess.TimeoutExpired:
            logger.error("FFmpeg compression timed out (1 hour limit)")
            raise APIError(
                "Video compression timed out - file may be too large",
                status_code=500
            )
        except Exception as e:
            logger.error(f"FFmpeg compression error: {str(e)}")
            
            # Clean up compressed file if compression failed
            if compressed_file_path and compressed_file_path.exists():
                try:
                    compressed_file_path.unlink()
                    logger.info(f"Cleaned up failed compressed file: {compressed_file_path}")
                except Exception as cleanup_e:
                    logger.error(f"Failed to cleanup compressed file: {str(cleanup_e)}")
            
            raise APIError(
                "Video compression failed",
                status_code=500,
                details=str(e)
            )
        
        # ===== Verify Compressed File =====
        if not compressed_file_path.exists():
            logger.error(f"Compressed file was not created: {compressed_file_path}")
            raise APIError(
                "Compressed file was not created successfully",
                status_code=500
            )
        
        compressed_size = compressed_file_path.stat().st_size
        
        if compressed_size == 0:
            logger.error(f"Compressed file is empty: {compressed_file_path}")
            try:
                compressed_file_path.unlink()
            except Exception as e:
                logger.error(f"Failed to cleanup empty compressed file: {str(e)}")
            
            raise APIError(
                "Compressed file is empty - compression failed",
                status_code=500
            )
        
        # Calculate compression ratio
        compression_ratio = (1 - (compressed_size / original_size)) * 100
        logger.info(
            f"Compression successful. "
            f"Original: {original_size / (1024*1024):.2f} MB, "
            f"Compressed: {compressed_size / (1024*1024):.2f} MB, "
            f"Saved: {compression_ratio:.1f}%"
        )
        
        return str(compressed_file_path)
    
    except APIError:
        raise
    
    except Exception as e:
        logger.exception(f"Unexpected error during video compression: {str(e)}")
        
        # Clean up compressed file on unexpected error
        if compressed_file_path and compressed_file_path.exists():
            try:
                compressed_file_path.unlink()
                logger.info(f"Cleaned up compressed file after error: {compressed_file_path}")
            except Exception as cleanup_e:
                logger.error(f"Failed to cleanup compressed file: {str(cleanup_e)}")
        
        raise APIError(
            "Unexpected error during video compression",
            status_code=500,
            details=str(e)
        )
