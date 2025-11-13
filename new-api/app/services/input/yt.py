from app.utils.logger import get_logger
from fastapi import HTTPException, status
from pathlib import Path
from datetime import datetime
from uuid import uuid4
from app.config import config
import yt_dlp

logger = get_logger(__name__)


def yt_mp3(link: str) -> Path:
    try:
        logger.debug("Stared for the yt_text")
        temp_mp3_path = (
            config.TEMP_DIR / f"{datetime.now().isoformat()}_{uuid4()}_temp.mp3"
        )

        try:
            logger.info("Started to download video and extracting audio")

            yt_opts = {
                "format": "bestaudio/best",
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192",
                    }
                ],
                "outtmpl": str(
                    temp_mp3_path.with_suffix("")
                ),  # Remove .mp3 extension as yt-dlp adds it
                "quiet": False,
                "no_warnings": False,
                "socket_timeout": 30,
                "http_chunk_size": 10485760,  # 10MB chunks
            }

            with yt_dlp.YoutubeDL(yt_opts) as ydl:
                info = ydl.extract_info(link, download=True)
                video_title = info.get("title", "video")
                logger.info(f"Successfully extracted audio from:{video_title}")

        except yt_dlp.utils.DownloadError as de:
            logger.error(f"Youtube download error: {str(de)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to dowload youtube video, video may be unavailable private, or restricted",
            )

        except yt_dlp.utils.ExtractorError as ee:
            logger.error(f"Youtube extractor error: {str(ee)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to extract audio from youtube video",
            )

        except Exception as e:
            logger.error(f"Youtube download error: {str(e)}")
            raise RuntimeError(f"Failed to download youtube audio: {str(e)}")

        actual_mp3_path = temp_mp3_path.with_suffix(".mp3")
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

        return actual_mp3_path

    except (ValueError, RuntimeError, HTTPException):
        raise

    except Exception as e:
        logger.error(f"Failed to convert the yt to mp3: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to convert the yt to mp3",
        )
