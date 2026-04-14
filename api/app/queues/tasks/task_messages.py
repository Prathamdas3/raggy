from uuid import UUID

from app.core import get_logger,celery

@celery.task(
    bind=True,
    max_retries=2,
    default_retry_delay=10,
    name="task_save_answer",
)
def task_save_answer(self,data:dict):
    question_id:str|None=data.get("question_id")
    answer:str|None=data.get("answer")
    if not question_id or not answer:
        raise ValueError("Invalid input missing answer or question_id")
    if not question_id.strip() or not answer.strip():
        raise ValueError("Invalid input empty question_id or answer")
    
    try:
        from app.core import get_celery_session
        # from app.services import
    except Exception as e:
        raise self.retry(exc=e)