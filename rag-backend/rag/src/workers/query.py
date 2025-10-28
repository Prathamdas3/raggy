from lib.celery import celery
from lib.logger import get_logger

logger=get_logger("workers/query")

@celery.task(bind=True,max_retries=3)
def HandleQuery():
    pass