from lib.celery import celery
from lib.logger import get_logger

logger = get_logger("workers/query")


@celery.task(bind=True, max_retries=3)
def handle_query(self, chat_id: str, user_id: str, question_id: str, question: str):
    try:
        if not chat_id or not user_id or not question or not question_id:
            logger.error("Missing parameters in handle_query task")
            return {
                "status": "error",
                "message": "missing paramerters",
                "code": 400,
                "data": None,
            }

        if (
            chat_id.strip() == ""
            or question.strip() == ""
            or question_id.strip() == ""
            or user_id.strip() == ""
        ):
            logger.error("Empty parameters in the handle_query task")
            return {
                "status": "error",
                "message": "Empty parameter is not allowed",
                "code": 400,
                "data": None,
            }

        if not isinstance(question, str):
            logger.error("Question must be string")
            return {
                "status": "error",
                "message": "Question is not string",
                "code": 400,
                "data": None,
            }

        question = question.strip()

        if len(question) < 10:
            logger.error("Question length too sort")
            return {"status": "error", "message": "question is too sort"}

        # ==== Get Vector Store =======
        try:
            from lib.qdrant import get_vector_store

            vector_store = get_vector_store()
            logger.info("✓ Vector store instance obtained")
        except Exception as vs_error:
            logger.error(f"✗ Failed to get vector store: {str(vs_error)}")
            return {
                "success": False,
                "error": f"Vector store error: {str(vs_error)}",
                "results": None,
            }

        try:
            from qdrant_client import models

            logger.info("Creating the retriver...")

            retriever = vector_store.similarity_search(
                query=question,
                k=1,
                filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="metadata.chat_id",
                            match=models.MatchValue(value=chat_id),
                        ),
                        models.FieldCondition(
                            key="metadata.user_id",
                            match=models.MatchValue(value=user_id),
                        ),
                    ]
                ),
            )

            logger.info("✓ MMR retriever created successfully")

            content = "\n".join([doc.page_content for doc in retriever])

            if not isinstance(content, str) or content.strip() == "":
                logger.error("Summary is empty after stripping")
                return {
                    "status": "error",
                    "message": "Content generation produced empty text",
                    "code": 500,
                    "data": None,
                }

            content = content.strip()

            try:
                logger.info("Generating answer using language model")
                from lib.query_model import get_response

                answer = get_response(query=content, question=question)

                if not answer:
                    logger.error("Answer generation returned empty result")
                    return {
                        "status": "error",
                        "code": 500,
                        "data": None,
                        "message": "Answer generation returned empty result",
                    }

                if not isinstance(answer, str):
                    logger.warning(f"Answer is not string: {type(answer)}, converting")
                    answer = str(answer)

                answer = answer.strip()

                if not answer:
                    logger.error("Answer is empty after stripping")
                    return {
                        "status": "error",
                        "message": "Answer generation produced empty text",
                        "code": 500,
                        "data": None,
                    }

                logger.info(
                    f"✓ Summary generation successful. Length: {len(answer)} characters"
                )

                # ==== store answer to db =======
                try:
                    from workers.db.store_answer import store_answer_to_db

                    if not answer or len(answer) == 0:
                        logger.error("Answer text is empty, cannot store to database")
                        return {
                            "status": "error",
                            "message": "Answer text is empty, cannot store to database",
                            "code": 500,
                            "data": None,
                        }

                    logger.info("Storing answer to database")

                    db_task_result = store_answer_to_db.delay(
                        chat_id=chat_id, question_id=question_id, content=answer
                    )

                    logger.info(
                        f"✓ Answer stored to database. Task ID: {db_task_result.id}"
                    )
                    audio_task_id = None
                    try:
                        logger.info("Triggering text-to-audio conversion task")
                        from workers.rag.answer_audio import convert_text_to_audio

                        if not chat_id or not question_id:
                            logger.warning(
                                "question_id or chat_id missing, skipping audio generation"
                            )
                        else:
                            # Trigger audio generation task

                            audio_task_result = convert_text_to_audio.delay(
                                text=answer, chat_id=chat_id, question_id=question_id
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

                except Exception as db_error:
                    logger.error(
                        f"✗ Failed to store summary to database: {str(db_error)}"
                    )
                    return {
                        "status": "partial_success",
                        "message": "Summary generated and audio task triggered, but failed to store in database",
                        "code": 206,
                        "data": {
                            "answer": answer,
                            "question": question,
                            "answer_length": len(answer),
                            "audio_task_id": audio_task_id,
                        },
                        "store_error": str(db_error),
                    }

            except Exception as answer_error:
                logger.error(f"Answer generation failed: {str(answer_error)}")
                return {
                    "status": "error",
                    "message": f"Answer generation failed: {str(answer_error)}",
                    "code": 500,
                    "data": None,
                }

        except Exception as retriever_error:
            logger.error(f"✗ Failed to create retriever: {str(retriever_error)}")
            logger.exception("Detailed error traceback:")
            return {
                "status": "error",
                "message": f"Failed to create retriever: {str(retriever_error)}",
                "code": 500,
                "data": None,
            }

    except Exception as e:
        logger.exception(f"✗ Unexpected error in handle query: {str(e)}")

        # Retry on unexpected errors
        if self.request.retries < self.max_retries:
            logger.info(
                f"Retrying task. Attempt {self.request.retries + 1}/{self.max_retries}"
            )
            raise self.retry(exc=e, countdown=30)

        return {
            "status": "error",
            "message": f"Unexpected error: {str(e)}",
            "code": 500,
            "data": None,
        }
