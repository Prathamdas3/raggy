
from lib.celery import celery
from langchain_text_splitters import RecursiveCharacterTextSplitter
from lib.logger import get_logger

logger = get_logger("text_splitter")

# Initialize text splitter once
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)


@celery.task(bind=True)
def split_text_task(self, text: str, user_id: str, chat_id: str) -> dict:
    """
    Split text into chunks with metadata (user_id and chat_id).

    Args:
        text: Text to split
        user_id: User ID making the request
        chat_id: Chat ID for context

    Returns:
        dict: {
            "status": "success"/"error",
            "data": {
                "chunks": [
                    {
                        "content": "chunk text...",
                        "metadata": {
                            "user_id": "user123",
                            "chat_id": "chat456",
                            "chunk_index": 0
                        }
                    },
                    ...
                ],
                "chunk_count": 5
            },
            "message": "...",
            "code": 200/400/500
        }
    """
    logger.info(
        f"Text splitting task started. User: {user_id}, Chat: {chat_id}, Text length: {len(text) if text else 0}"
    )

    try:
        # ===== Input Validation =====
        if not text:
            logger.error("Empty text provided for splitting")
            return {
                "status": "error",
                "message": "Text cannot be empty",
                "code": 400,
                "data": None,
            }

        if not isinstance(text, str):
            logger.error(f"Text must be string, received: {type(text)}")
            return {
                "status": "error",
                "message": "Text must be a string",
                "code": 400,
                "data": None,
            }

        text = text.strip()

        if not text:
            logger.error("Text is empty after stripping whitespace")
            return {
                "status": "error",
                "message": "Text cannot be empty or only whitespace",
                "code": 400,
                "data": None,
            }

        if not user_id:
            logger.error("User ID not provided")
            return {
                "status": "error",
                "message": "User ID is required",
                "code": 400,
                "data": None,
            }

        if not chat_id:
            logger.error("Chat ID not provided")
            return {
                "status": "error",
                "message": "Chat ID is required",
                "code": 400,
                "data": None,
            }

        # ===== Split Text =====
        logger.info(f"Starting text split. Input text length: {len(text)} characters")

        try:
            # Split text using LangChain's text splitter
            split_texts = text_splitter.split_text(text)

            if not split_texts:
                logger.warning(
                    f"Text splitter returned empty list for text of length: {len(text)}"
                )
                return {
                    "status": "error",
                    "message": "Failed to split text - no chunks created",
                    "code": 500,
                    "data": None,
                }

            logger.info(f"Text split successfully into {len(split_texts)} chunks")

        except Exception as e:
            logger.error(f"Error during text splitting: {str(e)}")
            return {
                "status": "error",
                "message": "Failed to split text",
                "code": 500,
                "data": None,
                "details": str(e),
            }

        # ===== Add Metadata to Each Chunk =====
        chunks_with_metadata = []

        for chunk_index, chunk_text in enumerate(split_texts):
            # Skip empty chunks
            if not chunk_text.strip():
                continue

            chunk_data = {
                "content": chunk_text,
                "metadata": {
                    "user_id": user_id,
                    "chat_id": chat_id,
                    "chunk_index": chunk_index,
                },
            }
            chunks_with_metadata.append(chunk_data)

        if not chunks_with_metadata:
            logger.warning("All chunks were empty after filtering")
            return {
                "status": "error",
                "message": "No valid text chunks created",
                "code": 400,
                "data": None,
            }

        logger.info(f"Created {len(chunks_with_metadata)} chunks with metadata")
        try:
            from workers.db.store_text_worker import send_chunks_to_docs_api_task
            logger.info(
                f"Starting the api calling with the chunks: {len(chunks_with_metadata)}"
            )
            task_data = send_chunks_to_docs_api_task.delay(
                user_id=user_id,chat_id=chat_id,chunks=chunks_with_metadata
            )
            logger.info(
                f"Queued storing the data task {task_data.id} for storing the text chunks"
            )

            logger.info(
                f"Text splitting task completed successfully. Chunks: {len(chunks_with_metadata)}"
            )
            return {
                "status": "success",
                "message": "Text split successfully with metadata and queued for db storing",
                "code": 200,
                "data": {
                    "chunks": chunks_with_metadata,
                    "chunk_count": len(chunks_with_metadata),
                    "original_text_length": len(text),
                },
            }
        except Exception as e:
            logger.error(f"Failed to queue for storing the text chunks in db")
            return {
                "status": "partial_success",
                "message": "Text splited successfully but failed to queue for db storing",
                "code": 206,
                "store_error": str(e),
            }

    except Exception as e:
        logger.exception(f"Unexpected error in text splitting task: {str(e)}")
        return {
            "status": "error",
            "message": "Unexpected error during text splitting",
            "code": 500,
            "data": None,
            "details": str(e),
        }
