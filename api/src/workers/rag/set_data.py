from lib.celery import celery
from lib.logger import get_logger
from lib.qdrant import get_vector_store
from typing import List, Dict, Any
from uuid import uuid4

logger = get_logger("workers/vectors/set_data")


@celery.task(bind=True, max_retries=3)
def save_chunks_to_vectorstore(self, chunks: List[Dict[str, Any]]):
    """
    Save chunks to Qdrant vector store with comprehensive error handling.

    Args:
        chunks: List of chunk dictionaries with 'content' and 'metadata' keys

    Returns:
        dict: Contains success status, document IDs, and any error messages
    """
    try:
        logger.info(f"Starting save operation for {len(chunks)} chunks")

        # ===== Validate Input =====
        if not chunks or not isinstance(chunks, list):
            logger.error("Invalid chunks provided: must be a non-empty list")
            return {
                "success": False,
                "error": "chunks must be a non-empty list",
                "document_ids": None,
                "saved_count": 0,
            }

        if len(chunks) == 0:
            logger.error("Empty chunks list provided")
            return {
                "success": False,
                "error": "chunks list is empty",
                "document_ids": None,
                "saved_count": 0,
            }

        # Validate each chunk structure
        for i, chunk in enumerate(chunks):
            if not isinstance(chunk, dict):
                logger.error(f"Chunk {i} is not a dictionary")
                return {
                    "success": False,
                    "error": f"Chunk at index {i} is not a dictionary",
                    "document_ids": None,
                    "saved_count": 0,
                }

            if "content" not in chunk:
                logger.error(f"Chunk {i} missing 'content' field")
                return {
                    "success": False,
                    "error": f"Chunk at index {i} missing 'content' field",
                    "document_ids": None,
                    "saved_count": 0,
                }

            if "metadata" not in chunk:
                logger.error(f"Chunk {i} missing 'metadata' field")
                return {
                    "success": False,
                    "error": f"Chunk at index {i} missing 'metadata' field",
                    "document_ids": None,
                    "saved_count": 0,
                }

            # Validate content
            content = chunk.get("content", "").strip()
            if not content:
                logger.error(f"Chunk {i} has empty content")
                return {
                    "success": False,
                    "error": f"Chunk at index {i} has empty content",
                    "document_ids": None,
                    "saved_count": 0,
                }

            # Validate metadata
            metadata = chunk.get("metadata", {})
            required_metadata = ["user_id", "chat_id", "chunk_index"]
            for field in required_metadata:
                if field not in metadata:
                    logger.error(f"Chunk {i} metadata missing '{field}' field")
                    return {
                        "success": False,
                        "error": f"Chunk at index {i} metadata missing '{field}' field",
                        "document_ids": None,
                        "saved_count": 0,
                    }

        logger.info(f"✓ All {len(chunks)} chunks validated successfully")

        # ===== Get Vector Store Instance =====
        try:
            vector_store = get_vector_store()
            logger.info("✓ Vector store instance obtained")
        except Exception as vs_error:
            logger.error(f"✗ Failed to get vector store: {str(vs_error)}")

            # Retry on vector store initialization failure
            if self.request.retries < self.max_retries:
                logger.info(
                    f"Retrying task. Attempt {self.request.retries + 1}/{self.max_retries}"
                )
                raise self.retry(exc=vs_error, countdown=30)

            return {
                "success": False,
                "error": f"Vector store error: {str(vs_error)}",
                "document_ids": None,
                "saved_count": 0,
            }

        # ===== Prepare Data for Vector Store =====
        texts = []
        metadatas = []
        ids = []

        for chunk in chunks:
            content = chunk["content"].strip()
            metadata = {
                "user_id": chunk["metadata"]["user_id"],
                "chat_id": chunk["metadata"]["chat_id"],
                "chunk_index": chunk["metadata"]["chunk_index"],
            }

            texts.append(content)
            metadatas.append(metadata)
            ids.append(str(uuid4()))

        logger.info(f"Prepared {len(texts)} texts for embedding")
        logger.info(f"Sample ID: {ids[0]}")
        logger.info(f"Sample metadata: {metadatas[0]}")

        # ===== Add Documents to Vector Store =====
        try:
            logger.info("Adding documents to vector store...")

            document_ids = vector_store.add_texts(
                texts=texts, metadatas=metadatas, ids=ids
            )

            logger.info(
                f"✓ Successfully added {len(document_ids)} documents to vector store"
            )

            # Log sample document IDs
            sample_ids = document_ids[:3] if len(document_ids) > 3 else document_ids
            logger.info(f"Sample document IDs: {sample_ids}")

            # Verify the count matches
            if len(document_ids) != len(chunks):
                logger.warning(
                    f"⚠ Document count mismatch. Expected: {len(chunks)}, Got: {len(document_ids)}"
                )

            return {
                "success": True,
                "error": None,
                "saved_count": len(document_ids),
                "total_requested": len(chunks),
            }

        except Exception as add_error:
            logger.error(f"✗ Failed to add documents to vector store: {str(add_error)}")
            logger.exception("Detailed error traceback:")

            # Retry on addition failure
            if self.request.retries < self.max_retries:
                logger.info(
                    f"Retrying task. Attempt {self.request.retries + 1}/{self.max_retries}"
                )
                raise self.retry(exc=add_error, countdown=60)

            return {
                "success": False,
                "error": f"Failed to add documents: {str(add_error)}",
                "document_ids": None,
                "saved_count": 0,
            }

    except Exception as e:
        logger.exception(f"✗ Unexpected error in save_chunks_to_vectorstore: {str(e)}")

        # Retry on unexpected errors
        if self.request.retries < self.max_retries:
            logger.info(
                f"Retrying task. Attempt {self.request.retries + 1}/{self.max_retries}"
            )
            raise self.retry(exc=e, countdown=60)

        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "document_ids": None,
            "saved_count": 0,
        }
