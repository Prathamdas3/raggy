from app.configs.celery import celery
from app.services.common.model import get_response
from app.utils.logger import get_logger
from app.schemas.input.yt import TaskInput

logger = get_logger(__name__)


@celery.task(bind=True, max_retries=3, default_retry_delay=10)
def task_generate_summary(self, data: dict) -> dict:
    """
    Celery task to generate summary and title from text.

    Args:
        data: Dictionary containing text and other metadata

    Returns:
        dict: Updated data with summary_text and title

    Raises:
        ValueError: If summary or title generation fails
    """
    # Validate and parse input
    try:
        data = TaskInput(**data)
    except Exception as e:
        logger.error(f"Invalid task input: {e}")
        raise ValueError(f"Invalid task input data: {e}")

    logger.info(f"Started summary generation task for text length: {len(data.text)}")
    logger.debug(f"Text preview: {data.text[:100]}...")

    try:
        # Generate summary and title
        logger.debug("Calling get_response for summary generation...")
        summary_text, title = get_response(query=data.text)

        # FIXED: Better validation with detailed logging
        if not summary_text or not summary_text.strip():
            logger.error("❌ Empty summary text returned")
            logger.error("This indicates the model generated no content")
            raise ValueError(
                "Failed to generate summary text - model returned empty response. "
                "Check model configuration and prompt formatting."
            )

        if not title or not title.strip():
            logger.error("❌ Empty title returned")
            logger.warning("Attempting to use fallback title...")

            # FIXED: Generate fallback title instead of failing
            title = _generate_fallback_title(data.text, summary_text)
            logger.debug(f"✓ Using fallback title: '{title}'")

        # Log success
        logger.debug("✓ Summary generated successfully")
        logger.debug(f"  Title: '{title}'")
        logger.debug(f"  Summary length: {len(summary_text)} chars")
        logger.debug(f"  Summary preview: {summary_text[:150]}...")

        # Build response
        details = data.model_dump()
        details["summary_text"] = summary_text.strip()
        details["title"] = title.strip()

        # FIXED: Validate final data before returning
        if not details.get("title"):
            logger.error("Title is missing in final details")
            raise ValueError("Title is missing after generation")

        if not details.get("summary_text"):
            logger.error("Summary is missing in final details")
            raise ValueError("Summary is missing after generation")

        logger.debug(f"✓ Task completed successfully - Title: '{details['title']}'")
        return details

    except ValueError as e:
        # Don't retry ValueError - these are unrecoverable
        logger.error(f"❌ ValueError in summary generation: {e}")
        raise

    except RuntimeError as e:
        # Model errors - these might be recoverable with retry
        logger.error(f"❌ RuntimeError in summary generation: {e}")
        logger.info(
            f"Retrying... (attempt {self.request.retries + 1}/{self.max_retries})"
        )
        raise self.retry(exc=e)

    except Exception as e:
        # Unexpected errors - retry with caution
        logger.error(
            f"❌ Unexpected error in summary generation: {e}",
            exc_info=True,
        )
        logger.info(
            f"Retrying... (attempt {self.request.retries + 1}/{self.max_retries})"
        )
        raise self.retry(exc=e)


def _generate_fallback_title(text: str, summary: str) -> str:
    """
    Generate a fallback title when model fails to provide one.

    Args:
        text: Original text
        summary: Generated summary

    Returns:
        str: Fallback title
    """
    # Try to use first sentence of summary
    sentences = summary.split(".")
    first_sentence = sentences[0].strip() if sentences else ""

    if first_sentence and 5 < len(first_sentence) < 100:
        logger.debug(f"Using first sentence of summary as title: {first_sentence}")
        return first_sentence

    # Try to use first line of original text
    lines = text.split("\n")
    first_line = lines[0].strip() if lines else ""

    if first_line and 5 < len(first_line) < 100:
        logger.debug(f"Using first line of text as title: {first_line}")
        return first_line

    # Last resort: generate generic title with timestamp
    from datetime import datetime

    fallback = f"Summary - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    logger.debug(f"Using timestamped fallback title: {fallback}")
    return fallback
