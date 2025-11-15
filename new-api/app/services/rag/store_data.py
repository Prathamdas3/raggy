from app.configs.qdrant import get_vector_store
from app.utils.logger import get_logger
from app.schemas.rag.text_spliter import ChunkData
from uuid import uuid4

logger = get_logger(__name__)


def save_vectorstore(chunks: list[ChunkData]):
    logger.debug("Started the process of the storing the chunks in the vector store")

    if not chunks or not isinstance(chunks, list):
        raise TypeError("Chunks should be a type of list")

    if len(chunks) == 0:
        raise ValueError("Content of chunks can not be empty")

    for i, chunk in enumerate(chunks):
        if not isinstance(chunk, dict):
            logger.error(f"Chunk {i} is not a dictionary")
            raise TypeError("chunk should be a type of dictionary")

        if "content" not in chunk:
            logger.error(f"Chunk {i} missing 'content' field")
            raise ValueError("chunk is missing teh content field")

        if "metadata" not in chunk:
            logger.error(f"Chunk {i} missing 'metadata' field")
            raise ValueError("chunk is missing the metadata field")

        # Validate content
        content = chunk.get("content", "").strip()
        if not content:
            logger.error(f"Chunk {i} has empty content")
            raise ValueError("chunk content is empty")

        metadata = chunk.get("metadata", {})
        required_metadata = ["user_id", "chat_id", "chunk_index"]
        for field in required_metadata:
            if field not in metadata:
                logger.error(f"Chunk {i} metadata missing '{field}' field")
                raise ValueError(f"chunk is missing the {field}")

    logger.debug(f"✓ All {len(chunks)} chunks validated successfully")

    try:
        vector_store = get_vector_store()
        logger.debug("Vector store instance obtained")

    except Exception as e:
        logger.error(f"Failed to get the vector store:{str(e)}")
        raise

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

    try:
        document_ids = vector_store.add_texts(texts=texts, metadatas=metadatas, ids=ids)

        logger.debug(
            f"✓ Successfully added {len(document_ids)} documents to vector store"
        )

        sample_ids = document_ids[:3] if len(document_ids) > 3 else document_ids
        logger.info(f"Sample document IDs: {sample_ids}")

        if len(document_ids) != len(chunks):
            logger.warning(
                f"⚠ Document count mismatch. Expected: {len(chunks)}, Got: {len(document_ids)}"
            )

    except Exception as e:
        logger.error(
            f"Failed to add document to the vector store:{str(e)}", exc_info=True
        )

        raise Exception("Failed to add the document")
