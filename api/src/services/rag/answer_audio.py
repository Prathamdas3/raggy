from lib.celery import celery
from lib.logger import get_logger
from gtts import gTTS
from pathlib import Path
from uuid import uuid4
from datetime import datetime


logger = get_logger("workers/answer_audio")

TEMP_DIR = Path("temp")
TEMP_DIR.mkdir(exist_ok=True)


@celery.task(bind=True)
def convert_text_to_audio(self, text: str, chat_id: str, question_id: str):
    """
    Convert text to audio file using gTTS, save to temp directory,
    and trigger MinIO upload task.

    Args:
        text: The text to convert to audio
        chat_id: The chat ID for organizing audio files
        question_id: The question Id to save the answer file


    Returns:
        dict: Contains success status, temp file path, and any error messages
    """

    temp_file_path = None

    try:
        logger.info(
            f"Starting text-to-audio conversion for the answer with question_id:{question_id}"
        )

        if not text or not isinstance(text, str):
            logger.error("Invalid text provided")
            return {
                "success": False,
                "error": "Invalid text provided",
                "temp_file_path": None,
            }

        if not chat_id or not isinstance(chat_id, str):
            logger.error("Invalid chat_id provided")
            return {
                "success": False,
                "error": "Invalid chat_id provided",
                "temp_file_path": None,
            }

        if not question_id or not isinstance(question_id, str):
            logger.error("Invalid question_id provided")
            return {
                "success": False,
                "error": "Invalid question_id provided",
                "temp_file_path": None,
            }

        max_chars = 50000
        if len(text) > max_chars:
            logger.warning(
                f"Text too long ({len(text)} chars), truncating to {max_chars}"
            )
            text = text[:max_chars]

            # Create unique filename
        unique_id = uuid4()
        timestamp = datetime.now().isoformat().replace(":", "-")
        temp_filename = f"audio_{timestamp}_{unique_id}.mp3"
        temp_file_path = TEMP_DIR / temp_filename

        try:
            tts = gTTS(text=text, lang="en", slow=False)
            tts.save(str(temp_file_path))
            logger.info(f"✓ gTTS conversion successful: {temp_file_path}")
        except Exception as tts_error:
            logger.error(f"✗ gTTS conversion failed: {str(tts_error)}")
            return {
                "success": False,
                "error": f"Text-to-speech conversion failed: {str(tts_error)}",
                "temp_file_path": None,
            }

        if not temp_file_path.exists():
            logger.error("✗ Temp audio file was not created")
            return {
                "success": False,
                "error": "Audio file creation failed",
                "temp_file_path": None,
            }

        file_size = temp_file_path.stat().st_size
        if file_size == 0:
            logger.error("✗ Created audio file is empty")
            temp_file_path.unlink()
            return {
                "success": False,
                "error": "Audio file is empty",
                "temp_file_path": None,
            }

        logger.info(
            f"✓ Text-to-audio conversion completed. File size: {file_size} bytes"
        )

        # ===== Trigger upload_audio_to_minio task =====
        logger.info(f"Triggering upload_audio_to_minio task for chat_id: {chat_id}")
        try:
            from workers.rag.upload_answer_audio_to_minio import upload_audio_to_minio

            # Call the upload task asynchronously
            upload_task_result = upload_audio_to_minio.delay(
                temp_file_path=str(temp_file_path),
                chat_id=chat_id,
                question_id=question_id,
            )

            logger.info(
                f"✓ upload_audio_to_minio task triggered. Task ID: {upload_task_result.id}"
            )

            return {
                "success": True,
                "error": None,
                "temp_file_path": str(temp_file_path),
                "file_size": file_size,
                "upload_task_id": upload_task_result.id,
            }

        except Exception as upload_task_error:
            logger.error(
                f"✗ Failed to trigger upload_audio_to_minio task: {str(upload_task_error)}"
            )

            # Clean up temp file since upload task failed to trigger
            try:
                temp_file_path.unlink()
                logger.info(
                    f"Cleaned up temp file after upload task failure: {temp_file_path}"
                )
            except Exception as cleanup_error:
                logger.error(f"Failed to cleanup temp file: {cleanup_error}")

            return {
                "success": False,
                "error": f"Failed to trigger upload task: {str(upload_task_error)}",
                "temp_file_path": None,
            }

    except Exception as e:
        logger.exception(f"✗ Unexpected error in convert_text_to_audio: {str(e)}")

        # Clean up temp file on error
        if temp_file_path and temp_file_path.exists():
            try:
                temp_file_path.unlink()
                logger.info(f"Cleaned up temp file after error: {temp_file_path}")
            except Exception as cleanup_error:
                logger.error(f"Failed to cleanup temp file: {cleanup_error}")

        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "temp_file_path": None,
        }
