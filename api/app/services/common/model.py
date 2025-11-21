from app.configs.model import get_model
from app.utils.logger import get_logger
from app.constants import MODEL_PROMPT_SUMMARY, MODEL_PROMPT_QUERY
from langchain_core.messages import HumanMessage, SystemMessage
from typing import Tuple

logger = get_logger(__name__)



def get_response(query: str, question: str | None = None) -> Tuple[str, str | None]:
    """Get response for the summary and optionally a title
    
    Returns:
        Tuple[str, str | None]: (summary, title) where title is None for query flow
    """
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
        parse_title = True
    else:
        messages = [
            SystemMessage(content=MODEL_PROMPT_QUERY),
            HumanMessage(content=f"Question: {question}\n\nQuery: {query}"),
        ]
        logger.debug("Using query flow")
        parse_title = False
    
    try:
        response = model.invoke(messages)
    except Exception as e:
        logger.error(f"Model invocation failed: {e}")
        raise
    
    if not response or not hasattr(response, "content"):
        raise RuntimeError("Invalid response from model")
    
    content = response.content

    content_str = str(content).strip() if content else ""
    
    if not content_str:
        return "", None
    
    # Parse title and summary for summary flow
    if parse_title:
        try:
            title, summary = _parse_title_and_summary(content_str)
            return summary, title
        except Exception as e:
            logger.warning(f"Failed to parse title from response: {e}")
            # Fallback: return full content with no title
            return content_str, None
    else:
        # Query flow: no title
        return content_str, None


def _parse_title_and_summary(content: str) -> Tuple[str, str]:
    """Parse title and summary from formatted response
    
    Args:
        content: Response content in format "TITLE: ...\nSUMMARY: ..."
    
    Returns:
        Tuple[str, str]: (title, summary)
    
    Raises:
        ValueError: If content cannot be parsed
    """
    
    title = ""
    summary = ""
    
    # Try to find TITLE: and SUMMARY: markers
    if 'TITLE:' in content and 'SUMMARY:' in content:
        title_start = content.find('TITLE:')
        summary_start = content.find('SUMMARY:')
        
        if title_start < summary_start:
            title = content[title_start + 6:summary_start].strip()
            summary = content[summary_start + 8:].strip()
        else:
            raise ValueError("Title and summary markers in wrong order")
    else:
        raise ValueError("Missing TITLE: or SUMMARY: markers")
    
    return title, summary