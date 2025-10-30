from lib.celery import celery
from lib.logger import get_logger
from lib.model import get_response


logger = get_logger("workers/summary")


@celery.task(bind=True)
def generate_summary(
    self, original_text: str, user_id: str = None, chat_id: str = None
):
    """
    Generate summary from text content and convert it to audio.

    Args:
        original_text: Plain text string to summarize
        user_id: Optional user ID for tracking
        chat_id: Optional chat ID for tracking

    Returns:
        dict: {"status": "success"/"error", "data": summary, "message": "...", "code": 200/400/500}
    """
    logger.info("Starting summary generation task")
    logger.info(f"User: {user_id}, Chat: {chat_id}")

    try:
        # ===== Input Validation =====
        if not original_text:
            logger.error("Empty text provided")
            return {
                "status": "error",
                "message": "No text provided for summary generation",
                "code": 400,
                "data": None,
            }

        if not isinstance(original_text, str):
            logger.error(f"Invalid text type: {type(original_text)}, expected string")
            return {
                "status": "error",
                "message": f"Text must be a string, received: {type(original_text)}",
                "code": 400,
                "data": None,
            }

        # Strip whitespace
        original_text = original_text.strip()

        if not original_text:
            logger.error("Text is empty after stripping whitespace")
            return {
                "status": "error",
                "message": "Text cannot be empty or only whitespace",
                "code": 400,
                "data": None,
            }

        text_length = len(original_text)
        logger.info(f"Processing text of length: {text_length} characters")

        # ===== Validate Content Length =====
        if text_length > 100000:  # 100k character limit
            logger.warning(
                f"Content very long ({text_length} chars), truncating to 100k"
            )
            original_text = original_text[:100000]
            text_length = 100000

        if text_length < 10:
            logger.warning(f"Content very short ({text_length} chars)")
            return {
                "status": "error",
                "message": "Text too short for meaningful summary (minimum 10 characters)",
                "code": 400,
                "data": None,
            }

        # ===== Generate Summary =====
        try:
            logger.info("Generating summary using language model")

            summary = get_response(query=original_text)

            # Validate summary
            if not summary:
                logger.error("Summary generation returned empty result")
                return {
                    "status": "error",
                    "message": "Summary generation returned empty result",
                    "code": 500,
                    "data": None,
                }

            if not isinstance(summary, str):
                logger.warning(f"Summary is not string: {type(summary)}, converting")
                summary = str(summary)

            summary = summary.strip()

            if not summary:
                logger.error("Summary is empty after stripping")
                return {
                    "status": "error",
                    "message": "Summary generation produced empty text",
                    "code": 500,
                    "data": None,
                }

            logger.info(
                f"✓ Summary generation successful. Length: {len(summary)} characters"
            )

            # ===== Trigger Audio Generation Task =====
            audio_task_id = None
            try:
                logger.info("Triggering text-to-audio conversion task")
                from workers.audio import convert_text_to_audio

                if not chat_id:
                    logger.warning(
                        " chat_id missing, skipping audio generation"
                    )
                else:
                    # Trigger audio generation task

                    audio_task_result = convert_text_to_audio.delay(
                        text=summary, chat_id=chat_id
                    )

                    audio_task_id = audio_task_result.id
                    logger.info(
                        f"✓ Audio generation task triggered. Task ID: {audio_task_id}"
                    )

            except Exception as audio_error:
                logger.error(
                    f"✗ Failed to trigger audio generation task: {str(audio_error)}"
                )
                # Continue with summary storage even if audio task fails
                logger.warning(
                    "Continuing with summary storage despite audio task failure"
                )

            # ===== Store Summary to Database =====
            try:
                from workers.db.store_summary import store_summary_to_db

                if not summary or len(summary) == 0:
                    logger.error("Summary text is empty, cannot store to database")
                    return {
                        "status": "error",
                        "message": "Summary text is empty, cannot store to database",
                        "code": 500,
                        "data": None,
                    }

                logger.info("Storing summary to database")
                db_task_result = store_summary_to_db.delay(
                    user_id=user_id, chat_id=chat_id, summary=summary
                )

                logger.info(
                    f"✓ Summary stored to database. Task ID: {db_task_result.id}"
                )

                return {
                    "status": "success",
                    "message": "Summary generated, audio task triggered, and summary stored successfully",
                    "code": 200,
                    "data": {
                        "summary": summary,
                        "original_length": text_length,
                        "summary_length": len(summary),
                        "audio_task_id": audio_task_id,
                        "db_task_id": db_task_result.id,
                    },
                }

            except Exception as db_error:
                logger.error(f"✗ Failed to store summary to database: {str(db_error)}")
                return {
                    "status": "partial_success",
                    "message": "Summary generated and audio task triggered, but failed to store in database",
                    "code": 206,
                    "data": {
                        "summary": summary,
                        "original_length": text_length,
                        "summary_length": len(summary),
                        "audio_task_id": audio_task_id,
                    },
                    "store_error": str(db_error),
                }

        except Exception as e:
            logger.error(f"✗ Summary generation failed: {str(e)}")
            return {
                "status": "error",
                "message": f"Summary generation failed: {str(e)}",
                "code": 500,
                "data": None,
            }

    except Exception as e:
        logger.exception(f"✗ Unexpected error in generate_summary task: {str(e)}")
        return {
            "status": "error",
            "message": f"Unexpected error during summary generation: {str(e)}",
            "code": 500,
            "data": None,
        }
