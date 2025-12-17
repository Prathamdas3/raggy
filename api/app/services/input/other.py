from app.utils.logger import get_logger
from app.utils.remove_file import remove_file
import fitz
from pathlib import Path
from docx import Document
from pptx import Presentation
from docx2python import docx2python

logger = get_logger(__name__)


def extract_text_from_pdf(file_path: Path) -> str:
    logger.debug(f"Extracting text from PDF file: {file_path}")
    text = ""
    doc = None

    try:
        # Open the PDF document
        doc = fitz.open(file_path)
        total_pages = doc.page_count
        logger.info(f"PDF opened successfully. Total pages: {total_pages}")

        # Iterate through all pages
        for page_num in range(total_pages):
            try:
                page = doc[page_num]
                page_text = page.get_text()

                if page_text.strip():
                    text += page_text
                    logger.debug(f"Extracted text from page {page_num + 1}")
                else:
                    logger.debug(f"Page {page_num + 1} is empty")

            except Exception as page_error:
                logger.error(
                    f"Error extracting text from page {page_num + 1}: {str(page_error)}"
                )
                # Continue with next page instead of failing completely
                continue

        if not text.strip():
            logger.warning(f"No text found in PDF: {file_path}")
            raise RuntimeError("No text content found in PDF")

        logger.info(
            f"Successfully extracted text from all {total_pages} pages of PDF: {file_path}"
        )
        return text.strip()

    except RuntimeError:
        raise

    except fitz.FileError:
        logger.error(f"Invalid PDF file: {file_path}")
        raise RuntimeError(f"Invalid or corrupted PDF file: {file_path}")

    except Exception as e:
        logger.exception(f"Error extracting text from PDF: {file_path}")
        raise RuntimeError(f"Failed to extract text from PDF: {str(e)}")

    finally:
        # Always close the document
        if doc is not None:
            try:
                doc.close()
                logger.debug(f"PDF document closed: {file_path}")
            except Exception as close_error:
                logger.warning(f"Error closing PDF document: {str(close_error)}")


def extract_text_from_plaintext(file_path: Path) -> str:
    logger.info(f"Extracting text from plain text file: {file_path}")
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            text = file.read()
        logger.info(f"Successfully extracted text from plain text: {file_path}")
        return text
    except Exception as e:
        logger.exception(f"Error extracting text from plain text: {file_path}")
        raise RuntimeError(f"Failed to extract text from plain text: {str(e)}")


def extract_text_from_docx(file_path: Path) -> str:
    logger.debug(f"Extracting text from DOCX file: {file_path}")
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

        logger.debug(f"Successfully extracted text from DOCX: {file_path}")
        return text
    except Exception as e:
        logger.exception(f"Error extracting text from DOCX: {file_path}")
        raise RuntimeError(f"Failed to extract text from DOCX: {str(e)}")


def extract_text_from_doc(file_path: Path) -> str:
    logger.debug(f"Extracting text from DOC file: {file_path}")
    try:
        result = docx2python(file_path)
        text = result.text
        logger.info(f"Successfully extracted text from DOC: {file_path}")
        return text
    except Exception as e:
        logger.exception(f"Error extracting text from DOC: {file_path}")
        raise RuntimeError(f"Failed to extract text from DOC: {str(e)}")


def extract_text_from_ppt(file_path: Path) -> str:
    logger.debug(f"Extracting text from PPT file: {file_path}")
    try:
        presentation = Presentation(file_path)
        text = ""

        for _, slide in enumerate(presentation.slides, 1):
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

        logger.debug(f"Successfully extracted text from PPT: {file_path}")
        return text
    except Exception as e:
        logger.exception(f"Error extracting text from PPT: {file_path}")
        raise RuntimeError(f"Failed to extract text from PPT: {str(e)}")


def handle_other_file(file_path: Path, file_type: str) -> str:
    logger.info(f"Starting text extraction: {file_path} of type {file_type}")

    if not file_path:
        raise ValueError("Empty file path provided")

    if not file_path.exists():
        raise FileNotFoundError(f"File does not exist: {file_path}")

    if not file_path.is_file():
        raise IsADirectoryError(f"Path is not a file: {file_path}")

    text = ""

    try:
        if file_type == "pdf":
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
            raise ValueError("Unsupported file type")

        logger.info(f"Text extraction completed: {file_path}")

        if not text or not text.strip():
            logger.warning(f"No text extracted from the file: {file_path}")
            raise ValueError("No text found from the given file")
    except ValueError:
        raise
    except Exception:
        raise

    try:
        remove_file(file_path)
    except Exception as e:
        # Non-fatal — WAV is already created
        logger.warning(f"Could not delete original file: {e}")
    return text
