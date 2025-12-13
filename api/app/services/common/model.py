from app.configs.model import get_model
from app.utils.logger import get_logger
from app.constants import MODEL_PROMPT_SUMMARY, MODEL_PROMPT_QUERY
from langchain_core.messages import HumanMessage, SystemMessage
from typing import Tuple

logger = get_logger(__name__)


def get_response(query: str, question: str | None = None) -> Tuple[str, str | None]:
    """
    Get response for the summary and optionally a title
    
    Args:
        query: The text to summarize or query against
        question: Optional question for query flow
    
    Returns:
        Tuple[str, str | None]: (summary, title) where title is None for query flow
        
    Raises:
        ValueError: If query is empty or invalid
        RuntimeError: If model fails to generate response
    """
    # Validation
    if not query or not query.strip():
        logger.error("Empty query provided")
        raise ValueError("Query cannot be empty")
    
    if not isinstance(query, str):
        raise TypeError("Query needs to be type of string")
    
    query = query.strip()
    
    # Get model instance
    try:
        model = get_model()
    except Exception as e:
        logger.error(f"Failed to get model: {e}")
        raise RuntimeError(f"Model initialization failed: {e}")
    
    # Determine flow and build messages
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
    
    # Invoke model with retry logic
    max_retries = 2
    response = None
    
    for attempt in range(max_retries):
        try:
            logger.debug(f"Attempt {attempt + 1}/{max_retries}")
            logger.debug(f"Input messages: {len(messages)} message(s)")
            logger.debug(f"First message preview: {str(messages[0])[:100]}...")
            
            # FIXED: Add configuration to invoke
            response = model.invoke(
                messages,
                max_tokens=2048,  # Ensure enough tokens
                temperature=0.7,
            )
            
            logger.debug(f"Response metadata: {response.response_metadata}")
            logger.debug(f"Token usage: {response.usage_metadata}")
            logger.debug(f"Content length: {len(response.content)} chars")
            
            # FIXED: Check for empty content
            if not response.content or len(response.content.strip()) == 0:
                logger.warning(f"⚠ Empty response on attempt {attempt + 1}")
                logger.warning(f"Finish reason: {response.response_metadata.get('finish_reason')}")
                
                if attempt < max_retries - 1:
                    logger.debug("Retrying with adjusted parameters...")
                    continue
                else:
                    raise RuntimeError(
                        "Model returned empty content after multiple attempts. "
                        "This may be a prompt formatting issue."
                    )
            
            # Success - break retry loop
            logger.debug(f"✓ Successfully got response: {response.content[:100]}...")
            break
            
        except Exception as e:
            logger.error(f"Model invocation failed on attempt {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                logger.debug("Retrying...")
                continue
            else:
                raise RuntimeError(f"Model invocation failed after {max_retries} attempts: {e}")
    
    # Validate response
    if not response or not hasattr(response, "content"):
        raise RuntimeError("Invalid response from model - missing content attribute")
    
    content = response.content
    content_str = str(content).strip() if content else ""
    
    if not content_str:
        logger.error("Model returned empty content")
        raise RuntimeError(
            "Model generated empty response. Check prompt formatting and model configuration."
        )
    
    logger.debug(f"Response content preview: {content_str[:200]}...")
    
    # Parse title and summary for summary flow
    if parse_title:
        try:
            title, summary = _parse_title_and_summary(content_str)
            logger.debug(f"✓ Parsed - Title: '{title[:50]}...', Summary length: {len(summary)}")
            return summary, title
            
        except ValueError as e:
            logger.warning(f"Failed to parse title from response: {e}")
            logger.warning("Response format doesn't match expected pattern")
            logger.warning(f"Content: {content_str[:200]}...")
            
            # FIXED: Better fallback handling
            # Try to extract something useful even if format is wrong
            title = _extract_fallback_title(content_str)
            summary = content_str
            
            logger.debug(f"Using fallback - Title: '{title}', Summary: content as-is")
            return summary, title
    else:
        # Query flow: no title
        logger.debug(f"✓ Query response length: {len(content_str)}")
        return content_str, None


def _parse_title_and_summary(content: str) -> Tuple[str, str]:
    """
    Parse title and summary from formatted response
    
    Args:
        content: Response content in format "TITLE: ...\nSUMMARY: ..."
    
    Returns:
        Tuple[str, str]: (title, summary)
        
    Raises:
        ValueError: If content cannot be parsed
    """
    title = ""
    summary = ""
    
    # Try to find TITLE: and SUMMARY: markers (case-insensitive)
    content_upper = content.upper()
    
    if "TITLE:" in content_upper and "SUMMARY:" in content_upper:
        title_start = content_upper.find("TITLE:")
        summary_start = content_upper.find("SUMMARY:")
        
        if title_start < summary_start:
            # Extract title (skip "TITLE:" prefix)
            title = content[title_start + 6 : summary_start].strip()
            # Extract summary (skip "SUMMARY:" prefix)
            summary = content[summary_start + 8 :].strip()
            
            # Clean up common artifacts
            title = title.strip('*"\'').strip()
            summary = summary.strip('*"\'').strip()
            
            if not title or not summary:
                raise ValueError("Title or summary is empty after parsing")
            
            logger.debug(f"Successfully parsed - Title: {title[:50]}..., Summary: {len(summary)} chars")
            return title, summary
        else:
            raise ValueError("Title and summary markers in wrong order")
    else:
        missing = []
        if "TITLE:" not in content_upper:
            missing.append("TITLE:")
        if "SUMMARY:" not in content_upper:
            missing.append("SUMMARY:")
        raise ValueError(f"Missing markers: {', '.join(missing)}")


def _extract_fallback_title(content: str) -> str:
    """
    Extract a fallback title from content when parsing fails
    
    Args:
        content: The response content
        
    Returns:
        str: Extracted or generated title
    """
    # Try to get first line as title
    lines = content.split('\n')
    first_line = lines[0].strip() if lines else ""
    
    # Remove common prefixes
    first_line = first_line.replace("Title:", "").replace("TITLE:", "").strip()
    first_line = first_line.strip('*"\'#').strip()
    
    # If first line is reasonable length, use it
    if first_line and 5 < len(first_line) < 100:
        logger.debug(f"Using first line as fallback title: {first_line}")
        return first_line
    
    # Otherwise, use first 50 chars of content
    fallback = content[:50].strip()
    if len(content) > 50:
        fallback += "..."
    
    logger.debug(f"Generated fallback title from content: {fallback}")
    return fallback