from pathlib import Path
from app.utils.file import remove_file
from app.utils.logger import get_logger
import tempfile
import subprocess
import os

logger = get_logger(__name__)


def audio_video_wav(path: Path) -> Path:
    file_path = Path(path)

    # ===== Basic Validations =====
    if not file_path:
        raise ValueError("Empty file path provided")

    if not file_path.exists():
        raise FileNotFoundError(f"File does not exist: {file_path}")

    if not file_path.is_file():
        raise IsADirectoryError(f"Path is not a file: {file_path}")

    wav_file_path = None

    # ===== Create Temporary WAV File =====
    try:
        temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False, dir="temp")
        wav_file_path = temp_file.name
        temp_file.close()
    except Exception as e:
        logger.error(f"Failed to create temporary WAV file: {e}")
        raise

    # ===== Run FFmpeg (extract audio from audio/video) =====
    command = [
        "ffmpeg",
        "-i",
        str(file_path),
        "-map",
        "0:a:0?",  # pick first audio stream if present
        "-vn",  # ignore video
        "-ac",
        "1",  # mono
        "-ar",
        "16000",  # 16kHz
        "-c:a",
        "pcm_s16le",  # WAV PCM
        "-y",
        wav_file_path,
    ]

    try:
        process = subprocess.run(command, capture_output=True, text=True, timeout=3600)
    except FileNotFoundError:
        # ffmpeg binary not found — ensure no temp file left
        if wav_file_path and os.path.exists(wav_file_path):
            try:
                remove_file(wav_file_path)
            except Exception:
                logger.warning("Failed to remove temp WAV after ffmpeg missing")
        raise RuntimeError("ffmpeg not found — install FFmpeg")
    except Exception as e:
        # Generic failure running ffmpeg — clean up temp file
        if wav_file_path and os.path.exists(wav_file_path):
            try:
                remove_file(wav_file_path)
            except Exception:
                logger.warning("Failed to remove temp WAV after ffmpeg execution error")
        logger.error(f"FFmpeg execution failed: {e}")
        raise

    # ===== Validate FFmpeg Output =====
    if process.returncode != 0:
        # Clean the broken temp file if created
        if wav_file_path and os.path.exists(wav_file_path):
            try:
                remove_file(wav_file_path)
            except Exception:
                logger.warning("Failed to remove temp WAV after ffmpeg error")
        raise Exception(f"FFmpeg error: {process.stderr.strip()}")

    if not os.path.exists(wav_file_path) or os.path.getsize(wav_file_path) == 0:
        # cleanup then raise
        if wav_file_path and os.path.exists(wav_file_path):
            try:
                remove_file(wav_file_path)
            except Exception:
                logger.warning("Failed to remove empty temp WAV")
        raise Exception("WAV output is missing or empty")

    # ===== Remove Original File =====
    try:
        remove_file(file_path)
    except Exception as e:
        # Non-fatal — WAV is already created
        logger.warning(f"Could not delete original file: {e}")

    return wav_file_path
