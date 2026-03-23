from app.core import celery
from app.utils import text_to_audio
from app.core import get_logger


logger = get_logger(__name__)


@celery.task(
    bind=True, name="task_generate_audio", max_retries=3, default_retry_delay=10
)
def task_generate_audio(self, data: dict) -> dict[str, str | None]:
    try:
        id = data.get("summary_id") or data.get("query_id")
        text=data.get("content")
        if not id or not text:
            raise ValueError("No related Id found")
        audio_url = text_to_audio(text=text, id=id)
        return_value = {
            **data,
            "audio_url": audio_url,
        }
        return return_value
    except ValueError:
        raise
    except RuntimeError as e:
        logger.error(f"Failed to generate audio task:{str(e)}")
        raise self.retry(exc=e)
