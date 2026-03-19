from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from dataclasses import dataclass


@dataclass
class FileContent:
    title: str
    content: str


def extract_pdf_content_from_path(path: Path)->FileContent:
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
        raise Exception
