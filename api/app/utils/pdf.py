"""PDF extraction utilities.

Provides functions for extracting text content from PDF files.
"""

from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from dataclasses import dataclass


@dataclass
class FileContent:
    """Data class for extracted file content.

    Attributes:
        title: Document title from PDF metadata.
        content: Extracted text content from all pages.
    """

    title: str
    content: str


def extract_pdf_content_from_path(path: Path) -> FileContent:
    """Extract text content from a PDF file.

    Uses langchain's PyPDFLoader to extract text from all pages
    and metadata from the first page.

    Args:
        path: Path to the PDF file.

    Returns:
        FileContent with title and extracted text.

    Raises:
        Exception: If PDF extraction fails.
    """
    try:
        loader = PyPDFLoader(file_path=path)
        documents = loader.load()
        title: str = (
            documents[0].metadata["title"] if documents[0].metadata["title"] else ""
        )
        content = ""
        for document in documents:
            content += f"{document.page_content.replace('\n', '')}"
        return FileContent(title=title, content=content)
    except Exception:
        raise Exception("Failed to extract content from PDF")
