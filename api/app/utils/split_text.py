from uuid import uuid4
from dataclasses import dataclass, field
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.core import get_logger

logger = get_logger(__name__)

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)


@dataclass
class SplitData:
    texts: list[str] = field(default_factory=list)
    metadatas: list[dict[str, int]] = field(default_factory=list)
    ids: list[str] = field(default_factory=list)


def text_split(text: str) -> SplitData:
    if not isinstance(text, str):
        raise TypeError("Text must be a string.")
    if not text.strip():
        raise ValueError("Text is empty.")
    try:
        chunks = text_splitter.split_text(text)
        result = SplitData()
        for index, chunk in enumerate(chunks):
            if not chunk.strip():
                continue
            result.texts.append(chunk)
            result.metadatas.append({"chunk_index": index})
            result.ids.append(str(uuid4()))
        return result
    except (TypeError, ValueError):
        raise
    except Exception as e:
        logger.error(f"Error during text splitting: {e}")
        raise Exception("Failed to split text.") from e