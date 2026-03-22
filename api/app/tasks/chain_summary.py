from celery import chain
from app.tasks.task_extract_text import task_extract_text,ExtractedDictType
from app.tasks.task_summary import task_spawn_parallel
from app.core import get_logger

logger=get_logger(__name__)

def summary_chain(data:ExtractedDictType):
    try:
        workflow=chain(task_extract_text.s(data),task_spawn_parallel.s())
        workflow.delay()
    except Exception as e:
        logger.error(f"Failed to start chain_input workflow: {e}", exc_info=True)
        # Optionally raise or return response for API usage
        raise