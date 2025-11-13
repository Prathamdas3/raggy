from app.configs.celery import Celery
from app.services.common.text_audio import text_audio
from app.services.minio_save import save_audio_minio
from app.utils.logger import get_logger
from app.schemas.input.yt import SpechInput

logger = get_logger(__name__)


@Celery.task(bind=True, max_retries=3, default_retry_delay=10)
def task_generate_audio(self, data=dict):
    data = SpechInput(**data)
    logger.debug(
        "Starting the task of audio generation and saving in minio from summary text"
    )

    try:
        temp_audio_path = text_audio(text=data.summary_text)

        if not temp_audio_path:
            raise ValueError("Failed to get the temp audio path")

        audio_url = save_audio_minio(temp_audio_path)

        if not audio_url:
            raise ValueError("Failed to get the minio audio url")

        details = data.model_dump()
        data["audio_url"] = audio_url
        return details.dict()

    except Exception as e:
        logger.debug(
            f"Error while processing Celery task(audio_generation): {e}",
            exc_info=True,
        )
        raise self.retry(exec=e)
