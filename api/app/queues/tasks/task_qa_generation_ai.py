from app.core import get_logger, celery, ai_model
from app.constants import MODEL_PROMPT_QUERY
from huggingface_hub.errors import HfHubHTTPError
from langchain_core.messages import HumanMessage, SystemMessage
import re

logger = get_logger(__name__)


def _extract_retry_after(error_message: str) -> float:
    match = re.search(r"try again in (\d+\.?\d*)s", str(error_message))
    return float(match.group(1)) + 1 if match else 10.0

@celery.task(
    bind=True,
    max_retries=10,
    default_retry_delay=10,
    name="task_generate_answer",
)
def task_generate_answer(self, data: dict):
    question = data.get("question")
    context = data.get("context")
    if not question or  not context:
        raise ValueError("Invalid input for the the answer generation")

    if not question.strip() or  not context.strip():
        raise ValueError("Invalid input passed empty input in the answer generation")

    try:
        messages = [
            SystemMessage(content=MODEL_PROMPT_QUERY),
            HumanMessage(content=f"Question: {question} Text to use: {context}"),
        ]
        response=ai_model.invoke(messages=messages)
        return {**data,"answer":str(response.content).strip()}
    except HfHubHTTPError as e:
        error_str=str(e)
        if "429" in error_str:
            wait_time=_extract_retry_after(error_str)
            raise self.retry(
                    exc=e,
                    countdown=wait_time,
                )
        if "413" in error_str:
            raise self.retry(exc=e, countdown=10)
    
    except Exception as e:
        self.retry(exc=e)
