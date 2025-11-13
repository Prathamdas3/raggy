from app.configs.celery import celery
from app.schemas.input.yt import TaskInput, YTInput
from app.services.common.wav_converter import mp3_wav
from app.services.common.wav_text import wav_text
from app.services.input.yt import yt_mp3
from app.utils.logger import get_logger

logger = get_logger(__name__)


@celery.task(bind=True, max_retries=3, default_retry_delay=10)
def task_yt(self, data: dict):
    """Celery task for extracting the details from yt link, and coverteding them to text as well as to store them"""
    data = YTInput(**data)
    logger.debug("starting the task to convert the yt link to wav")

    try:
        mp3_link = yt_mp3(link=data.link)
        if not mp3_link:
            raise ValueError("MP3 conversion failed")

        wav_link = mp3_wav(mp3_link)
        if not wav_link:
            raise ValueError("Wav link conversion failed")

        text_wav = wav_text(wav_link)
        if not text_wav:
            raise ValueError("Text generation failed from wav")

        save_text_db = TaskInput(
            chat_id=data.chat_id, user_id=data.user_id, text=text_wav
        )

        return save_text_db.model_dump().dict()

    except Exception as e:
        logger.error(f"Error while processing Celery task(yt): {e}", exc_info=True)
        raise self.retry(exc=e)
