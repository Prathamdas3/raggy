from app.core import get_logger, celery, ai_model
from app.constants import MODEL_PROMPT_CHUNK_SUMMARY, MODEL_PROMPT_FINAL_SUMMARY
from huggingface_hub.errors import HfHubHTTPError
from langchain_core.messages import HumanMessage, SystemMessage
import time
import re
from app.utils import parse_title_and_summary

logger = get_logger(__name__)

MAX_CHUNK_CHARS = 4000


def _extract_retry_after(error_message: str) -> float:
    """Extract wait time from rate limit error message."""
    match = re.search(r"try again in (\d+\.?\d*)s", str(error_message))
    return float(match.group(1)) + 1 if match else 10.0


def split_into_chunks(content: str, chunk_size: int = MAX_CHUNK_CHARS) -> list[str]:
    """Split content into chunks at sentence boundaries."""
    if len(content) <= chunk_size:
        return [content]

    chunks = []
    current_chunk = ""

    for sentence in content.replace("\n", " ").split("."):
        sentence = sentence.strip()
        if not sentence:
            continue
        if len(current_chunk) + len(sentence) + 1 <= chunk_size:
            current_chunk += sentence + ". "
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence + ". "

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks


@celery.task(
    bind=True,
    max_retries=10,
    default_retry_delay=10,
    name="task_generate_summary_and_title",
)
def task_generate_summary_and_title(self, data: dict) -> dict:
    content = data.get("content")
    if not content or not content.strip():
        raise ValueError("No content passed for generating summary.")

    chunks = split_into_chunks(content)
    logger.info(f"Content split into {len(chunks)} chunks.")

    # ── Resume from where we left off ────────────────────────────
    # completed summaries carried through retries
    chunk_summaries: list[str] = data.get("_chunk_summaries", [])
    start_index = len(chunk_summaries)  # skip already completed chunks

    if start_index > 0:
        logger.info(f"Resuming from chunk {start_index + 1}/{len(chunks)}")

    # ── Process remaining chunks ──────────────────────────────────
    for i in range(start_index, len(chunks)):
        logger.info(f"Summarizing chunk {i + 1}/{len(chunks)}")

        if i > start_index:
            time.sleep(5)  # rate limit buffer between chunks

        try:
            chunk_messages = [
                SystemMessage(content=MODEL_PROMPT_CHUNK_SUMMARY),
                HumanMessage(content=chunks[i]),
            ]
            chunk_response = ai_model.invoke(messages=chunk_messages)
            chunk_summaries.append(str(chunk_response.content).strip())

        except HfHubHTTPError as e:
            error_str = str(e)
            if "429" in error_str:
                wait_time = _extract_retry_after(error_str)
                logger.warning(f"Rate limited at chunk {i + 1} — retrying in {wait_time}s")
                # ← save progress into data before retrying
                raise self.retry(
                    exc=e,
                    countdown=wait_time,
                    kwargs={"data": {**data, "_chunk_summaries": chunk_summaries}},
                )
            if "413" in error_str:
                raise ValueError(f"Chunk {i + 1} too large for model.") from e
            raise self.retry(exc=e, countdown=10)
        except Exception as e:
            logger.error(f"Failed on chunk {i + 1}: {e}")
            raise self.retry(
                exc=e,
                countdown=10,
                kwargs={"data": {**data, "_chunk_summaries": chunk_summaries}},
            )

    # ── All chunks done — generate final summary ──────────────────
    logger.info("All chunks summarized. Generating final summary.")

    final_content = (
        chunks[0] if len(chunks) == 1
        else "\n\n".join(f"Part {i + 1}:\n{s}" for i, s in enumerate(chunk_summaries))
    )

    try:
        time.sleep(5)  # buffer before final call
        response = ai_model.invoke(messages=[
            SystemMessage(content=MODEL_PROMPT_FINAL_SUMMARY),
            HumanMessage(content=final_content),
        ])
    except HfHubHTTPError as e:
        error_str = str(e)
        if "429" in error_str:
            wait_time = _extract_retry_after(error_str)
            logger.warning(f"Rate limited on final summary — retrying in {wait_time}s")
            raise self.retry(
                exc=e,
                countdown=wait_time,
                kwargs={"data": {**data, "_chunk_summaries": chunk_summaries}},
            )
        raise self.retry(exc=e, countdown=10)
    except Exception as e:
        logger.error(f"Final summary generation failed: {e}")
        raise self.retry(
            exc=e,
            countdown=10,
            kwargs={"data": {**data, "_chunk_summaries": chunk_summaries}},
        )

    # ── Parse and return ──────────────────────────────────────────
    try:
        content_str = str(response.content).strip()
        if not content_str:
            raise ValueError("Model returned empty response.")

        title, summary = parse_title_and_summary(content=content_str)
        logger.info("Successfully generated summary and title.")

        # clean up internal state before returning
        result = {k: v for k, v in data.items() if k != "_chunk_summaries"}
        return {**result, "content": summary, "title": title}

    except ValueError as e:
        logger.error(f"Failed to parse model response: {e}. Raw: {str(response.content)[:200]}")
        raise

