from app.utils.logger import get_logger
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.schemas.rag.text_spliter import ChunkData, SplitTextArgs


logger = get_logger(__name__)
text_spliter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)


def split_text(data: SplitTextArgs)->list[ChunkData]:
    try:
        split_text = text_spliter.split_text(data.text)

        if len(split_text) == 0:
            raise ValueError("Failed to generate splited text for empty value")
    except Exception as e:
        logger.error(f"Error during text spliting:{str(e)}")
        raise Exception("Failed to create splited text")

    chunks_with_metadata = []

    for chunk_index, chunk_text in enumerate(split_text):
        # Skip empty chunks
        if not chunk_text.strip():
            continue

        chunk_data = {
            "content": chunk_text,
            "metadata": {
                "user_id": data.user_id,
                "chat_id": data.chat_id,
                "chunk_index": chunk_index,
            },
        }
        chunks_with_metadata.append(chunk_data)

    if len(chunks_with_metadata) == 0:
        logger.warning("All chunks were empty after filtering")
        raise Exception("All chunks were empty after filtering")

    logger.debug("Successfully created the text chunks")
    return chunks_with_metadata
