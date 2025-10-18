from utils.files.delete import delete_file
from lib.celery import celery
from lib.pydentic_models import ErrorResponse
from lib.logger import get_logger
import fitz  # pymupdf
import os
from docx import Document
from pptx import Presentation
from docx2python import docx2python
from langchain_text_splitters import RecursiveCharacterTextSplitter

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

logger = get_logger("utils/extractors/others")


def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract text from PDF files.

    Args:
        file_path: Path to the PDF file

    Returns:
        Extracted text from all pages
    """
    logger.info(f"Extracting text from PDF file: {file_path}")
    text = ""
    try:
        doc = fitz.open(file_path)
        for page_num, page in enumerate(doc, 1):
            page_text = page.get_text()
            if page_text:
                text += page_text + "\n"
        logger.info(f"Successfully extracted text from PDF: {file_path}")
        return text
    except Exception as e:
        logger.exception(f"Error extracting text from PDF: {file_path}")
        raise RuntimeError(f"Failed to extract text from PDF: {str(e)}")


def extract_text_from_docx(file_path: str) -> str:
    """
    Extract text from DOCX files.

    Args:
        file_path: Path to the DOCX file

    Returns:
        Extracted text from the document
    """
    logger.info(f"Extracting text from DOCX file: {file_path}")
    try:
        doc = Document(file_path)
        text = ""

        # Extract text from paragraphs
        for para in doc.paragraphs:
            if para.text.strip():
                text += para.text + "\n"

        # Extract text from tables
        for table in doc.tables:
            for row in table.rows:
                row_text = " | ".join([cell.text for cell in row.cells])
                if row_text.strip():
                    text += row_text + "\n"

        logger.info(f"Successfully extracted text from DOCX: {file_path}")
        return text
    except Exception as e:
        logger.exception(f"Error extracting text from DOCX: {file_path}")
        raise RuntimeError(f"Failed to extract text from DOCX: {str(e)}")


def extract_text_from_doc(file_path: str) -> str:
    """
    Extract text from older DOC files.

    Args:
        file_path: Path to the DOC file

    Returns:
        Extracted text from the document
    """
    logger.info(f"Extracting text from DOC file: {file_path}")
    try:
        result = docx2python(file_path)
        text = result.text
        logger.info(f"Successfully extracted text from DOC: {file_path}")
        return text
    except Exception as e:
        logger.exception(f"Error extracting text from DOC: {file_path}")
        raise RuntimeError(f"Failed to extract text from DOC: {str(e)}")


def extract_text_from_ppt(file_path: str) -> str:
    """
    Extract text from PPT/PPTX files.

    Args:
        file_path: Path to the PPT/PPTX file

    Returns:
        Extracted text from all slides
    """
    logger.info(f"Extracting text from PPT file: {file_path}")
    try:
        presentation = Presentation(file_path)
        text = ""

        for slide_num, slide in enumerate(presentation.slides, 1):
            text += f"--- Slide {slide_num} ---\n"

            # Extract text from shapes
            for shape in slide.shapes:
                if hasattr(shape, "text") and shape.text.strip():
                    text += shape.text + "\n"

                # Extract text from tables
                if shape.has_table:
                    table = shape.table
                    for row in table.rows:
                        row_text = " | ".join([cell.text for cell in row.cells])
                        if row_text.strip():
                            text += row_text + "\n"

        logger.info(f"Successfully extracted text from PPT: {file_path}")
        return text
    except Exception as e:
        logger.exception(f"Error extracting text from PPT: {file_path}")
        raise RuntimeError(f"Failed to extract text from PPT: {str(e)}")


def extract_text_from_plaintext(file_path: str) -> str:
    """
    Extract text from plain text files.

    Args:
        file_path: Path to the text file

    Returns:
        Text content from the file
    """
    logger.info(f"Extracting text from plain text file: {file_path}")
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            text = file.read()
        logger.info(f"Successfully extracted text from plain text: {file_path}")
        return text
    except Exception as e:
        logger.exception(f"Error extracting text from plain text: {file_path}")
        raise RuntimeError(f"Failed to extract text from plain text: {str(e)}")


@celery.task(bind=True)
def extract_text_from_othertypes(self, file_path: str, file_type: str):
    """
    Extract text from supported file types.
    Returns a standardized response with extracted text.

    Supported types:
    - application/pdf
    - application/vnd.openxmlformats-officedocument.wordprocessingml.document (DOCX)
    - application/msword (DOC)
    - application/vnd.ms-powerpoint (PPT)
    - application/vnd.openxmlformats-officedocument.presentationml.presentation (PPTX)
    - text/plain
    """
    logger.info(f"Starting text extraction: {file_path} of type {file_type}")

    if not os.path.exists(file_path):
        logger.error(f"File does not exist: {file_path}")
        return ErrorResponse(status="error", message="File not found", code=404)

    try:
        text = ""

        if file_type == "application/pdf":
            text = extract_text_from_pdf(file_path)

        elif (
            file_type
            == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ):
            text = extract_text_from_docx(file_path)

        elif file_type == "application/msword":
            text = extract_text_from_doc(file_path)

        elif file_type in [
            "application/vnd.ms-powerpoint",
            "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        ]:
            text = extract_text_from_ppt(file_path)

        elif file_type == "text/plain":
            text = extract_text_from_plaintext(file_path)

        else:
            logger.warning(f"Unsupported file type: {file_type}")
            return ErrorResponse(
                status="error", message=f"Unsupported file type: {file_type}", code=400
            )

        logger.info(f"Text extraction completed: {file_path}")

        try:
            import asyncio

            logger.info(f"Deleting file after extraction: {file_path}")
            asyncio.run(delete_file(file_path))
            logger.info(f"File deleted successfully: {file_path}")
        except Exception as de:
            # Log warning but don't fail - extraction succeeded
            logger.warning(f"Failed to delete file: {str(de)}")
        return {
            "status": "success",
            "message": "Text extracted successfully",
            "code": 200,
            "data": {"text": text, "file_type": file_type},
        }

    except RuntimeError as re:
        logger.error(f"Runtime error extracting text from file: {file_path}: {str(re)}")
        return ErrorResponse(status="error", message=str(re), code=500)

    except Exception as e:
        logger.exception(f"Unexpected error extracting text from file: {file_path}")
        return ErrorResponse(
            status="error", message=f"Unexpected error: {str(e)}", code=500
        )
