from app.configs.celery import celery
from app.schemas.input.yt import YTInput
from app.utils.logger import get_logger

logger = get_logger(__name__)


@celery.task(bind=True)
def task_yt(self, data: YTInput):
    """Celery task for extracting the details from yt link, and coverteding them to text as well as to store them"""
    pass
