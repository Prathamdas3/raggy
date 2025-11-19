from app.configs.celery import celery
from app.services.common.text_audio import text_audio
from app.services.common.minio_save import upload_to_minio
from app.utils.logger import get_logger
from app.schemas.input.yt import SpechInput

logger = get_logger(__name__)


@celery.task(bind=True, max_retries=3, default_retry_delay=10)
def task_generate_audio(self, data=dict) -> dict:
    data = SpechInput(**data)
    logger.debug(
        "Starting the task of audio generation and saving in minio from summary text"
    )

    try:
        temp_audio_path = text_audio(text=data.summary_text)

        if not temp_audio_path:
            raise ValueError("Failed to get the temp audio path")

        audio_url = upload_to_minio(file_path=temp_audio_path, chat_id=data.chat_id,folder="audio",content_type="audio/mpeg")

        if not audio_url:
            raise ValueError("Failed to get the minio audio url")

        details = data.model_dump()
        details["audio_url"] = audio_url
        return details
    except Exception as e:
        logger.debug(
            f"Error while processing Celery task(audio_generation): {e}",
            exc_info=True,
        )
        raise self.retry(exc=e)
