from app.configs.model import get_model
from app.utils.logger import get_logger
from app.constants import MODEL_PROMPT_SUMMARY, MODEL_PROMPT_QUERY
from langchain_core.messages import HumanMessage, SystemMessage

logger = get_logger(__name__)


def get_response(query: str, question: str | None = None) -> str:
    """Get reponse for the summary"""
    if not query or not query.strip():
        logger.error("Empty query provided")
        raise ValueError("Query can not be empty")

    if not isinstance(query, str):
        raise TypeError("Query needs to be type of string")

    query = query.strip()

    try:
        model = get_model()
    except Exception:
        raise

    if not question or not question.strip():
        messages = [
            SystemMessage(content=MODEL_PROMPT_SUMMARY),
            HumanMessage(content=query),
        ]
        logger.debug("Using summary flow")
    else:
        messages = [
            SystemMessage(content=MODEL_PROMPT_QUERY),
            HumanMessage(content=f"Question: {question}\n\nQuery: {query}"),
        ]
        logger.debug("Using query flow")

    try:
        response = model.invoke(messages)
    except Exception as e:
        logger.error(f"Model invocation failed: {e}")
        raise

    if not response or not hasattr(response, "content"):
        raise RuntimeError("Invalid response from model")

    content = response.content
    return str(content).strip() if content else ""
