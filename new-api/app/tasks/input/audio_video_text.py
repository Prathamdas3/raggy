from app.configs.celery import celery
from app.schemas.input.file import OtherInput
from app.schemas.input.yt import TaskInput
from app.services.common.wav_text import wav_text
from app.services.input.audio_video import audio_video_wav
from app.utils.logger import get_logger

logger = get_logger(__name__)


@celery.task(bind=True, max_retries=3, default_retry_delay=10)
def task_audio_video_text(self, data: dict):
    data = OtherInput(**data)
    logger.debug("starting the task to convert the audio or video into text")

    try:
        wav_path = audio_video_wav(path=data.path)
        if not wav_path:
            raise ValueError("Wav conversion failed")

        wav_path_text = wav_text(wav_path)
        if not wav_path_text or not wav_path_text.strip():
            raise ValueError("Wav to text conversion failed")

        save_text_db = TaskInput(
            chat_id=data.chat_id, user_id=data.user_id, text=wav_path_text
        )

        return save_text_db.model_dump()

    except Exception as e:
        logger.error(
            f"Error while processing Celery task(audio_video_text): {str(e)}",
            exc_info=True,
        )

        raise self.retry(exc=e)
