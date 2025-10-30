from utils.files.delete import delete_file
from lib.celery import celery
from lib.logger import get_logger
import fitz  # pymupdf
import os
from docx import Document
from pptx import Presentation
from docx2python import docx2python
from langchain_text_splitters import RecursiveCharacterTextSplitter

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

logger = get_logger("workers/documents")


def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract text from all pages of a PDF file.

    Args:
        file_path: Path to the PDF file

    Returns:
        Extracted text from all pages
    """
    logger.info(f"Extracting text from PDF file: {file_path}")
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

                if page_text.strip():  # Only add if page has content
                    # Add page marker for clarity
                    text += f"\n--- Page {page_num + 1} ---\n"
                    text += page_text
                    logger.info(f"Extracted text from page {page_num + 1}")
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

    except FileNotFoundError:
        logger.error(f"PDF file not found: {file_path}")
        raise RuntimeError(f"PDF file not found: {file_path}")

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
def extract_text_from_othertypes(
    self, file_path: str, file_type: str, user_id: str, chat_id: str
):
    """
    Extract text from supported file types and queue for text splitting.

    Process:
    1. Extract text from document (PDF, DOCX, DOC, PPT, PPTX, TXT)
    2. Delete the source file
    3. Queue the extracted text for splitting into chunks

    Returns:
        dict: {"status": "success"/"error", "data": {...}, "message": "...", "code": 200/400/500}

    Supported types:
    - application/pdf
    - application/vnd.openxmlformats-officedocument.wordprocessingml.document (DOCX)
    - application/msword (DOC)
    - application/vnd.ms-powerpoint (PPT)
    - application/vnd.openxmlformats-officedocument.presentationml.presentation (PPTX)
    - text/plain
    """
    logger.info(
        f"Starting text extraction: {file_path} of type {file_type}, User: {user_id}, Chat: {chat_id}"
    )

    # ===== Input Validation =====
    if not file_path:
        logger.error("Empty file path provided")
        return {
            "status": "error",
            "message": "File path cannot be empty",
            "code": 400,
            "data": None,
        }

    if not file_type:
        logger.error("File type not provided")
        return {
            "status": "error",
            "message": "File type must be specified",
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

    if not os.path.exists(file_path):
        logger.error(f"File does not exist: {file_path}")
        return {
            "status": "error",
            "message": "File not found",
            "code": 404,
            "data": None,
        }

    try:
        # ===== Extract Text =====
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
            return {
                "status": "error",
                "message": f"Unsupported file type: {file_type}",
                "code": 400,
                "data": None,
            }

        logger.info(f"Text extraction completed: {file_path}")

        # Validate extracted text
        if not text or not text.strip():
            logger.warning(f"No text extracted from file: {file_path}")
            return {
                "status": "error",
                "message": "No text found in document",
                "code": 400,
                "data": None,
            }

        # ===== Delete File After Extraction =====
        try:
            import asyncio

            logger.info(f"Deleting file after extraction: {file_path}")
            asyncio.run(delete_file(file_path))
            logger.info(f"File deleted successfully: {file_path}")
        except Exception as de:
            # Log warning but don't fail - extraction succeeded
            logger.warning(f"Failed to delete file: {str(de)}")

        # ===== Queue Text for Splitting =====
        logger.info(f"Queueing text for splitting. Text length: {len(text)} characters")

        try:
            from workers.text_splitter import split_text_task

            split_task = split_text_task.delay(text, user_id, chat_id)
            logger.info(f"Queued split_text_task {split_task.id} for extracted text")

            return {
                "status": "success",
                "message": "Text extracted and queued for splitting",
                "code": 200,
                "data": {
                    "file_type": file_type,
                    "text_length": len(text),
                    "split_task_id": split_task.id,
                },
            }

        except Exception as se:
            logger.error(f"Failed to queue split_text_task: {str(se)}")
            return {
                "status": "partial_success",
                "message": "Text extracted successfully but failed to queue for splitting",
                "code": 206,  # 206 Partial Content
                "data": {
                    "file_type": file_type,
                    "text_length": len(text),
                    "extracted_text": text,
                    "split_error": str(se),
                },
            }

    except RuntimeError as re:
        logger.error(f"Runtime error extracting text from file: {file_path}: {str(re)}")
        return {"status": "error", "message": str(re), "code": 500, "data": None}

    except Exception as e:
        logger.exception(f"Unexpected error extracting text from file: {file_path}")
        return {
            "status": "error",
            "message": f"Unexpected error: {str(e)}",
            "code": 500,
            "data": None,
        }
