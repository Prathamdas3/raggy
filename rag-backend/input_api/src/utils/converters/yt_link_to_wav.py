from uuid import uuid4
from pathlib import Path
from datetime import datetime
import asyncio
import subprocess
import yt_dlp
from constants import YT_REGEX
from utils.response import APIError
from lib.logger import get_logger

logger = get_logger("utils/file/save_youtube")

TEMP_DIR = Path("temp")
TEMP_DIR.mkdir(exist_ok=True)



async def save_youtube_audio_as_wav(youtube_url: str) -> Path:
    """
    Download YouTube video, extract audio, and save as WAV file with unique naming.
    
    Args:
        youtube_url: Valid YouTube URL
        
    Returns:
        Path: Full path to the saved WAV file
        
    Raises:
        ValueError: If YouTube URL is invalid
        RuntimeError: If download or conversion fails
        APIError: If audio extraction fails
    """
    logger.info(f"Initiating save_youtube_audio_as_wav function for: {youtube_url}")
    
    # ===== Input Validation =====
    if not youtube_url:
        logger.error("Empty YouTube URL provided")
        raise ValueError("YouTube URL cannot be empty")
    
    youtube_url = youtube_url.strip()
    
    if not isinstance(youtube_url, str):
        logger.error("YouTube URL must be a string")
        raise ValueError("YouTube URL must be a string")
    
    if not YT_REGEX.match(youtube_url):
        logger.error(f"Invalid YouTube URL format: {youtube_url}")
        raise ValueError("Invalid YouTube URL format")
    
    logger.info(f"YouTube URL is valid: {youtube_url}")
    
    # ===== Create Unique WAV Filename =====
    # Using same naming convention as save_temp_file
    unique_name = f"{datetime.now().isoformat()}_{uuid4()}_youtube_audio.wav"
    wav_file_path = TEMP_DIR / unique_name
    
    # Temporary MP3 path (intermediate file)
    temp_mp3_path = TEMP_DIR / f"{datetime.now().isoformat()}_{uuid4()}_temp.mp3"
    
    logger.info(f"WAV file will be saved to: {wav_file_path}")
    logger.info(f"Temporary MP3 path: {temp_mp3_path}")
    
    try:
        # ===== Step 1: Download and Extract Audio as MP3 =====
        logger.info("Step 1: Downloading YouTube video and extracting audio")
        
        try:
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'outtmpl': str(temp_mp3_path.with_suffix('')),  # Remove .mp3 extension as yt-dlp adds it
                'quiet': False,
                'no_warnings': False,
                'socket_timeout': 30,
                'http_chunk_size': 10485760,  # 10MB chunks
            }
            
            logger.info("Downloading and converting YouTube video to MP3")
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(youtube_url, download=True)
                video_title = info.get('title', 'video')
                logger.info(f"Successfully extracted audio from: {video_title}")
        
        except yt_dlp.utils.DownloadError as de:
            logger.error(f"YouTube download error: {str(de)}")
            raise APIError(
                "Failed to download YouTube video. Video may be unavailable, private, or restricted.",
                status_code=400,
                details=str(de)
            )
        
        except yt_dlp.utils.ExtractorError as ee:
            logger.error(f"YouTube extractor error: {str(ee)}")
            raise APIError(
                "Failed to extract audio from YouTube video",
                status_code=500,
                details=str(ee)
            )
        
        except Exception as e:
            logger.error(f"YouTube download error: {str(e)}")
            raise RuntimeError(f"Failed to download YouTube audio: {str(e)}")
        
        # ===== Verify MP3 File Created =====
        actual_mp3_path = temp_mp3_path.with_suffix('.mp3')
        if not actual_mp3_path.exists():
            logger.error(f"MP3 file was not created: {actual_mp3_path}")
            raise RuntimeError("MP3 file was not created successfully")
        
        mp3_size = actual_mp3_path.stat().st_size
        if mp3_size == 0:
            logger.error(f"MP3 file is empty: {actual_mp3_path}")
            try:
                actual_mp3_path.unlink()
            except Exception as e:
                logger.error(f"Failed to cleanup empty MP3: {str(e)}")
            raise RuntimeError("MP3 file created but is empty")
        
        logger.info(f"MP3 file verified. Size: {mp3_size / (1024*1024):.2f} MB")
        
        # ===== Step 2: Convert MP3 to WAV =====
        logger.info("Step 2: Converting MP3 to WAV format")
        
        try:
            ffmpeg_command = [
                "ffmpeg",
                "-i", str(actual_mp3_path),
                "-codec:a", "pcm_s16le",  # WAV codec for high quality
                "-ar", "44100",           # Sample rate: 44.1kHz
                "-ac", "2",               # Audio channels: Stereo
                "-y",                     # Overwrite without asking
                str(wav_file_path)
            ]
            
            logger.info(f"Running FFmpeg command to convert MP3 to WAV")
            
            process = await asyncio.to_thread(
                subprocess.run,
                ffmpeg_command,
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour timeout
            )
            
            if process.returncode != 0:
                logger.error(f"FFmpeg error: {process.stderr}")
                raise RuntimeError(f"FFmpeg conversion failed: {process.stderr}")
            
            logger.info("FFmpeg conversion to WAV completed successfully")
        
        except subprocess.TimeoutExpired:
            logger.error("FFmpeg conversion timed out")
            raise RuntimeError("WAV conversion timed out - file may be too large")
        
        except FileNotFoundError:
            logger.error("FFmpeg not found on system")
            raise RuntimeError("FFmpeg is not installed - required for WAV conversion")
        
        except Exception as e:
            logger.error(f"FFmpeg conversion error: {str(e)}")
            raise RuntimeError(f"Failed to convert MP3 to WAV: {str(e)}")
        
        # ===== Verify WAV File =====
        if not wav_file_path.exists():
            logger.error(f"WAV file was not created: {wav_file_path}")
            raise RuntimeError("WAV file was not created successfully")
        
        wav_size = wav_file_path.stat().st_size
        
        if wav_size == 0:
            logger.error(f"WAV file is empty: {wav_file_path}")
            try:
                wav_file_path.unlink()
            except Exception as e:
                logger.error(f"Failed to cleanup empty WAV: {str(e)}")
            raise RuntimeError("WAV file created but is empty")
        
        logger.info(f"WAV file verified. Size: {wav_size / (1024*1024):.2f} MB")
        
        # ===== Clean up Temporary MP3 =====
        try:
            logger.info(f"Cleaning up temporary MP3 file: {actual_mp3_path}")
            actual_mp3_path.unlink()
            logger.info("Temporary MP3 file deleted")
        except Exception as e:
            logger.warning(f"Failed to cleanup temporary MP3: {str(e)}")
        
        logger.info(f"Successfully saved YouTube audio as WAV: {wav_file_path}")
        return wav_file_path
    
    except (ValueError, RuntimeError, APIError):
        raise
    
    except Exception as e:
        logger.exception(f"Unexpected error saving YouTube audio: {str(e)}")
        
        # Clean up files on error
        try:
            if wav_file_path.exists():
                wav_file_path.unlink()
                logger.info(f"Cleaned up WAV file after error: {wav_file_path}")
        except Exception as cleanup_e:
            logger.error(f"Failed to cleanup WAV file: {str(cleanup_e)}")
        
        try:
            actual_mp3_path = temp_mp3_path.with_suffix('.mp3')
            if actual_mp3_path.exists():
                actual_mp3_path.unlink()
                logger.info(f"Cleaned up MP3 file after error: {actual_mp3_path}")
        except Exception as cleanup_e:
            logger.error(f"Failed to cleanup MP3 file: {str(cleanup_e)}")
        
        raise RuntimeError(f"Failed to save YouTube audio: {str(e)}")