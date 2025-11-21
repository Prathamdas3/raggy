from app.utils.logger import get_logger
from app.configs.celery import celery
from app.schemas.rag.query import AnswerInput, QueryInput
from app.services.rag.generate_answer import generate_answer
from app.schemas.input.yt import SpechInput

logger = get_logger(__name__)


@celery.task(bind=True, max_retries=3, default_retry_delay=10)
def task_generate_answer(self, data: dict) -> dict:
    new_data = AnswerInput(**data)
    logger.debug("starting the task of answer generation")
    try:
        query_data = QueryInput(
            chat_id=new_data.chat_id,
            user_id=new_data.user_id,
            question=new_data.question,
        )
        answer,_ = generate_answer(data=query_data)
        if not answer or not answer.strip():
            raise ValueError("No answer found,it might be empty")

        details = SpechInput(
            user_id=new_data.user_id,
            chat_id=new_data.chat_id,
            question_id=new_data.question_id,
            summary_text=answer,
        )
        return details.model_dump()

    except Exception as e:
        logger.debug(
            f"Error while processing Celery task(answer_generation): {e}",
            exc_info=True,
        )
        raise self.retry(exc=e)
