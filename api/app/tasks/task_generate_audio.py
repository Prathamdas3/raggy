from app.core import celery
from app.utils import text_to_audio
from app.core import get_logger
from app.tasks.task_summary import UpdateSummaryArgs


logger = get_logger(__name__)


@celery.task(
    bind=True, name="task_generate_audio", max_retries=3, default_retry_delay=10
)
def task_generate_audio(self, content: str, summary_id: str):
    try:
        audio_url = text_to_audio(text=content, chat_id=summary_id)
        return_value:UpdateSummaryArgs={"audio_url":audio_url,"summary_id":summary_id,"content":None}
        return return_value
    except Exception as e:
        logger.error(f"Failed to generate audio task:{str(e)}")
        raise self.retry(exc=e)
