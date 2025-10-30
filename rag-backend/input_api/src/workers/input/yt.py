from lib.celery import celery
from utils.response import APIError
from lib.logger import get_logger
from utils.converters.yt_link_to_wav import save_youtube_audio_as_wav
from utils.converters.wav_to_text import transcribe_audio

logger = get_logger("utils/extractors/yt_link")


@celery.task(bind=True)
def extract_text_from_yt_link(
    self, link: str, user_id: str = None, chat_id: str = None
) -> dict:
    """
    Celery task to process a YouTube link, extract text, and queue for splitting.

    Process:
    1. Download and save YouTube video audio as WAV
    2. Transcribe WAV audio to text
    3. Queue extracted text for splitting into chunks
    4. Return extraction result and split task ID

    Args:
        link: YouTube video URL
        user_id: Optional user ID for tracking
        chat_id: Optional chat ID for tracking

    Returns:
        dict: {
            "status": "success"/"error"/"partial_success",
            "data": {
                "extracted_text": "...",
                "wav_file_path": "...",
                "split_task_id": "..." (if splitting queued),
                "user_id": "...",
                "chat_id": "..."
            },
            "message": "...",
            "code": 200/400/500/206
        }
    """
    logger.info(f"Celery task started: extract_text_from_yt_link")
    logger.info(f"Link: {link}, User: {user_id}, Chat: {chat_id}")

    wav_file_path = None

    # Set defaults for user_id and chat_id if not provided
    user_id = user_id or "unknown"
    chat_id = chat_id or "unknown"

    try:
        # ===== Input Validation =====
        if not link:
            logger.error("Empty YouTube link provided")
            return {
                "status": "error",
                "message": "YouTube link cannot be empty",
                "code": 400,
                "data": None,
            }

        link = link.strip()
        logger.info(f"Processing YouTube link: {link}")

        # ===== Step 1: Save YouTube Audio as WAV =====
        logger.info("Step 1: Saving YouTube audio as WAV")

        try:
            import asyncio

            wav_file_path = asyncio.run(save_youtube_audio_as_wav(link))
            logger.info(f"WAV file saved successfully at: {wav_file_path}")

        except APIError as ae:
            logger.error(f"WAV saving failed: {ae.message}")
            return {
                "status": "error",
                "message": f"WAV saving failed: {ae.message}",
                "code": ae.status_code,
                "data": None,
            }

        except Exception as ve:
            logger.error(f"Invalid YouTube link: {str(ve)}")
            return {
                "status": "error",
                "message": f"Invalid YouTube link: {str(ve)}",
                "code": 400,
                "data": None,
            }

        # ===== Step 2: Transcribe WAV to Text =====
        logger.info("Step 2: Transcribing WAV audio to text")

        try:
            import asyncio

            transcribed_text = asyncio.run(transcribe_audio(wav_file_path))
            logger.info(
                f"Transcription successful. Text length: {len(transcribed_text)} characters"
            )

        except APIError as ae:
            logger.error(f"Transcription failed: {ae.message}")
            return {
                "status": "error",
                "message": f"Transcription failed: {ae.message}",
                "code": ae.status_code,
                "data": None,
            }

        except Exception as e:
            logger.error(f"Unexpected error during transcription: {str(e)}")
            return {
                "status": "error",
                "message": "Unexpected error during transcription",
                "code": 500,
                "data": None,
            }

        # ===== Step 3: Queue Text for Splitting =====
        logger.info("Step 3: Queueing text for splitting")

        split_task_id = None
        split_error = None

        try:
            from workers.text_splitter import split_text_task

            split_task = split_text_task.delay(transcribed_text, user_id, chat_id)
            split_task_id = split_task.id
            logger.info(f"Queued split_text_task {split_task_id} for extracted text")

        except Exception as se:
            logger.error(f"Failed to queue split_text_task: {str(se)}")
            split_error = str(se)

        # ===== Return Response =====
        logger.info("extract_text_from_yt_link completed")

        if split_task_id:
            logger.info(
                f"Extraction and splitting successful. Split task ID: {split_task_id}"
            )
            return {
                "status": "success",
                "message": "Text extracted and queued for splitting successfully",
                "code": 200,
                "data": {
                    "extracted_text": transcribed_text,
                    "wav_file_path": str(wav_file_path),
                    "file_type": "yt_link, audio/wav",
                    "split_task_id": split_task_id,
                    "text_length": len(transcribed_text),
                },
            }
        else:
            # Extraction succeeded but splitting failed
            logger.warning(f"Extraction succeeded but splitting failed: {split_error}")
            return {
                "status": "partial_success",
                "message": "Text extracted successfully but failed to queue for splitting",
                "code": 206,  # 206 Partial Content
                "data": {
                    "extracted_text": transcribed_text,
                    "wav_file_path": str(wav_file_path),
                    "file_type": "yt_link, audio/wav",
                    "split_error": split_error,
                    "text_length": len(transcribed_text),
                },
            }

    except Exception as e:
        logger.exception(f"Unexpected error in extract_text_from_yt_link: {str(e)}")
        return {
            "status": "error",
            "message": "Unexpected server error",
            "code": 500,
            "data": None,
        }
