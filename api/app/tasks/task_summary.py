from uuid import UUID

from app.tasks.task_save_text import task_save_original_text_vector_db,SaveArgs
from app.core import get_logger,celery
from app.core import ai_model
from celery import group
from typing import TypedDict

logger=get_logger(__name__)

class UpdateSummaryArgs(TypedDict):
    summary_id:str
    audio_url:str|None
    content:str|None

class CreateSummaryReturn(TypedDict):
    summary_id:str
    content:str

@celery.task(
    bind=True,
    max_retries=3,
    default_retry_delay=10,
    name="task_create_summary",
)
def task_create_summary(self, data: SaveArgs)->CreateSummaryReturn:
    try:
        from app.db import get_celery_session,VariantType
        from app.services import get_summary_service
        with get_celery_session() as session:
            summary=get_summary_service(session=session)
            summary_id=summary.create_summary(chat_id=UUID(data.get("chat_id")),variant_type=VariantType.default)
            return_value:CreateSummaryReturn={"summary_id":str(summary_id),"content":data.get("content")}
            return return_value
    except Exception as e:
        logger.error(f"Failed to store the original text in the vector db: {str(e)}")
        raise self.retry(exc=e)
    

@celery.task(
    bind=True,
    max_retries=3,
    default_retry_delay=10,
    name="task_update_summary",
)
def task_update_summary(self, data: UpdateSummaryArgs) -> str:
    """
    Works for both cases:
    - updating content:   {"summary_id": "...", "content": "..."}
    - updating audio_url: {"summary_id": "...", "audio_url": "..."}
    - updating both:      {"summary_id": "...", "content": "...", "audio_url": "..."}
    """
    try:
        from app.db import get_celery_session
        from app.services import get_summary_service
        with get_celery_session() as session:
            service = get_summary_service(session=session)
            return service.update_summary(data=data)
    except Exception as e:
        logger.error(f"Failed to update summary: {e}")
        raise self.retry(exc=e)


@celery.task(
    bind=True,
    max_retries=3,
    default_retry_delay=10,
    name="task_update_title",
)
def task_update_title(self, data: UpdateSummaryArgs) -> str:
    try:
        from app.db import get_celery_session
        from app.services import get_chat_service
        with get_celery_session() as session:
            service = get_chat_service(session=session)
            return service.update_chat(chat_id=)
    except Exception as e:
        logger.error(f"Failed to update summary: {e}")
        raise self.retry(exc=e)


@celery.task(
    bind=True,
    max_retries=3,
    default_retry_delay=10,
    name="task_update_summary",
)
def task_generate_summary(self,data:CreateSummaryReturn):
    try:
        
    except Exception as e:
        logger.error(f"Failed to generate the summary")
        raise self.retry(exc=e)
    

@celery.task(max_retries=3,default_retry_delay=10,name="task_update_summary",bind=True)
def task_spawn_parallel(self,data:SaveArgs):
    try:
        group(task_save_original_text_vector_db(),)
    except Exception as e:
        logger.error(f"Failed to process the parallel tasks: {str(e)}")
        raise self.retry(exc=e)


