from io import BytesIO
from dataclasses import dataclass
from pypdf import PdfReader
from app.core import get_logger,minio_client


logger = get_logger(__name__)


@dataclass
class FileContent:
    content: str


def extract_pdf_content(storage_key: str) -> FileContent:
    try:
        bucket_name, object_name = storage_key.split("/", 1)
        pdf_bytes = minio_client.get_file(
            bucket_name=bucket_name,
            object_name=object_name,
        )
        reader = PdfReader(BytesIO(pdf_bytes))
        content = " ".join(
            page.extract_text().replace("\n", " ")
            for page in reader.pages
            if page.extract_text()
        )
        if not content.strip():
            raise ValueError("No content extracted from PDF.")
        return FileContent(content=content)
    except ValueError:
        raise
    except Exception as e:
        logger.error(f"Failed to extract content from '{storage_key}': {e}")
        raise RuntimeError(f"Failed to extract PDF content: {e}") from e