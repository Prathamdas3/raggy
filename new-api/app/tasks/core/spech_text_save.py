from app.configs.celery import Celery
from app.schemas.db.docs import UpdateDocsData
from app.schemas.input.yt import SpechInput
from app.services.common.text_audio import text_audio
from app.services.db.docs import update_docs
from app.services.minio_save import save_audio_minio
from app.utils.logger import get_logger

logger = get_logger(__name__)


@Celery.task(bind=True, max_retries=3, default_retry_delay=10)
def task_spech_text_save(self, data: SpechInput):
    logger.debug("Starting the task of converting the spech to text and save it")

    try:
        temp_audio_path = text_audio(text=data.summary_text)

        if not temp_audio_path:
            raise ValueError("Failed to get the temp audio path")

        audio_url = save_audio_minio(temp_audio_path)
        save_summary_and_audio = UpdateDocsData(
            user_id=data.user_id,
            chat_id=data.chat_id,
            summary_text=data.summary_text,
            audio_url=audio_url,
        )
        update_docs(save_summary_and_audio)

    except Exception:
        raise
