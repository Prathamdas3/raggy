from datetime import datetime
from pathlib import Path
from app.config import config
from uuid import uuid4
from app.utils.logger import get_logger
import subprocess
from app.utils.file import remove_file

logger = get_logger(__name__)


def mp3_wav(path: Path) -> Path:
    try:
        unique_name = f"{datetime.now().isoformat()}_{uuid4()}_youtube_audio.wav"
        wav_file_path = config.TEMP_DIR / unique_name
        try:
            logger.info("started to convert the audio to mp3 to wav")
            unique_name = f"{datetime.now().isoformat()}_{uuid4()}_yt_audio.wav"
            wav_file_path = config.TEMP_DIR / unique_name
            ffmpeg_command = [
                "ffmpeg",
                "-i",
                str(path),
                "-codec:a",
                "pcm_s16le",  # WAV codec for high quality
                "-ar",
                "44100",  # Sample rate: 44.1kHz
                "-ac",
                "2",  # Audio channels: Stereo
                "-y",  # Overwrite without asking
                str(wav_file_path),
            ]
            logger.info("Running FFmpeg command to convert MP3 to WAV")

            process = subprocess.run(
                ffmpeg_command, capture_output=True, text=True, timeout=3600
            )

            if process.returncode != 0:
                logger.error(f"FFmpeg error: {process.stderr}")
                raise RuntimeError(f"FFmpeg conversion failed: {process.stderr}")

        except subprocess.TimeoutExpired:
            logger.error("FFmpeg conversion timed out")
            raise RuntimeError("WAV conversion timed out - file may be too large")

        except FileNotFoundError:
            logger.error("FFmpeg not found on system")
            raise RuntimeError("FFmpeg is not installed - required for WAV conversion")

        except Exception as e:
            logger.error(f"FFmpeg conversion error: {str(e)}")
            raise RuntimeError(f"Failed to convert MP3 to WAV: {str(e)}")

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

        logger.info(f"WAV file verified. Size: {wav_size / (1024 * 1024):.2f} MB")

        remove_file(file_path=path)

        return wav_file_path

    except RuntimeError:
        raise

    except Exception as e:
        logger.error(f"Failed to convert the yt to mp3: {str(e)}")
        raise
