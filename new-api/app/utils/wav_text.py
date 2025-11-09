from app.utils.logger import get_logger
from pathlib import Path
from app.configs.whisper import get_whisper_model
from fastapi import HTTPException, status
from app.utils.file import remove_file

logger = get_logger(__name__)


def wav_text(path: Path) -> str:
    audio_path = Path(path)

    if not str(audio_path).strip():
        logger.error("Empty file path provided")
        raise ValueError("Fail path cannot be empty")

    # Check if the path exists
    if not audio_path.exists():
        logger.warning(f"File does not exist: {audio_path}")
        raise FileNotFoundError(f"File does not exist: {audio_path}")

    # Check if it's actually a file (not a directory)
    if not audio_path.is_file():
        logger.error(f"Path is not a file: {audio_path}")
        raise IsADirectoryError(f"Path is a directory, not a file: {audio_path}")

    if audio_path.suffix.lower() != ".wav":
        logger.warning(f"File is not a wav file: {audio_path}")

    try:
        logger.info("Retriving whisper model instance")
        model = get_whisper_model()

        if model is None:
            logger.error("whisper model is none")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to init whisper model",
            )

        extracted_text = model.transcribe(str(audio_path), language="en")

        if not extracted_text or "text" not in extracted_text:
            logger.error("Invalid transcription result format")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to extract the text",
            )

        extracted_text = extracted_text["text"].strip()

        if not extracted_text:
            logger.warning("Transcript resulted in empty text")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No ")

        remove_file(str(audio_path))

        logger.info("Transcription completed")

        return extracted_text

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Unexpected error during transcription: {str(e)}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )
