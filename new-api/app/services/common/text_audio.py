from app.utils.logger import get_logger
from uuid import uuid4
from app.config import config
from datetime import datetime
from fastapi import HTTPException, status
from gtts import gTTS
from pathlib import Path

logger = get_logger(__name__)


def text_audio(text: str) -> Path:
    temp_file_path = None

    if not text or not isinstance(text, str):
        raise TypeError("text should be string")

    unique_id = uuid4()
    timestamp = datetime.now().isoformat().replace(":", "-")
    temp_filename = f"audio_{timestamp}_{unique_id}.mp3"
    temp_file_path = config.TEMP_DIR / temp_filename

    logger.debug(f"Creating audio file at: {temp_file_path}")

    try:
        tts = gTTS(text=text, lang="en", slow=False)
        tts.save(str(temp_file_path))
        logger.debug(f"gtts conversion sccessful: {temp_file_path}")
    except Exception as e:
        logger.error(f"gtts conversion failed:{str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to convert the text to audio",
        )

    if not temp_file_path.exists():
        raise FileNotFoundError("No files found after audio creation")

    file_size = temp_file_path.stat().st_size
    if file_size == 0:
        logger.error("Created audio file is empty")
        raise ValueError(f"No data found in the file with path: {temp_file_path}")

    return temp_file_path
