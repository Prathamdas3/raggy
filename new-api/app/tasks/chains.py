from celery import chain
from app.utils.logger import get_logger
from app.schemas.rag.query import AnswerInput
from app.schemas.input.yt import YTInput
from app.tasks.pipeline.save_original_text import task_save_original_text
from app.tasks.pipeline.save_vector_store import task_save_vector_store
from app.tasks.pipeline.generate_summary import task_generate_summary
from app.tasks.pipeline.generate_audio import task_generate_audio
from app.tasks.pipeline.update_db import task_update_db
from app.tasks.input.yt_text import task_yt
from app.tasks.rag.generate_answer import task_generate_answer

logger = get_logger(__name__)


def chain_input_link(data: YTInput):
    try:
        # Step 1: Convert the Pydantic model to dict
        payload = data.model_dump()

        # Step 2: Build the task chain
        workflow = chain(
            task_yt.s(payload),
            task_save_original_text.s(),
            task_save_vector_store.s(),
            task_generate_summary.s(),
            task_generate_audio.s(),
            task_update_db.s(),
        )

        # Step 3: Run the chain asynchronously
        workflow.apply_async()
        logger.info(
            f"Started chain_input workflow for: {payload.get('chat_id', 'unknown')}"
        )

    except Exception as e:
        logger.error(f"Failed to start chain_input workflow: {e}", exc_info=True)
        # Optionally raise or return response for API usage
        raise


def chain_answer(data: AnswerInput):
    try:
        payload = data.model_dump().dic()
        workflow = chain(
            task_generate_answer.s(payload), task_generate_audio.s(), task_update_db.s()
        )
        workflow.apply_async()
        logger.info(
            f"Started chain_answer workflow for: {payload.get('question_id', 'unknown')}"
        )
    except Exception as e:
        logger.error(f"Failed to start chain_yt workflow: {e}", exc_info=True)
        # Optionally raise or return response for API usage
        raise
