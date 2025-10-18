from pathlib import Path
from constants import ALLOWED_IMAGE_TYPES
from utils.converters.images_to_png import convert_image_to_png
from utils.response import APIError
from utils.files.delete import delete_file
from lib.logger import get_logger
from PIL import Image
import pytesseract

logger = get_logger("utils/converters/png_to_text")


async def extract_text_from_image(image_file_path: str, file_type: str) -> str:
    """
    Extract text from image files using OCR (Tesseract).

    Process:
    1. Convert image to PNG format
    2. Extract text from PNG using OCR
    3. Delete the PNG file after extraction

    Supports:
    - JPEG, JPG, PNG, WebP, BMP, GIF, TIFF

    Args:
        image_file_path: Path to the image file
        file_type: MIME type of the image

    Returns:
        str: Extracted text from the image

    Raises:
        APIError: With appropriate status codes for different failure scenarios:
            - 400: Invalid input, unsupported format, no text found
            - 404: File not found
            - 500: Conversion/IO/OCR errors
    """
    image_file_path = Path(image_file_path)
    png_file_path = None

    logger.info(
        f"Starting text extraction from image. File: {image_file_path}, Type: {file_type}"
    )

    try:
        # ===== Input Validation =====
        if not image_file_path:
            logger.error("Empty image file path provided")
            raise APIError("Image file path cannot be empty", status_code=400)

        if not image_file_path.exists():
            logger.error(f"Image file does not exist: {image_file_path}")
            raise APIError(f"Image file not found: {image_file_path}", status_code=404)

        if not image_file_path.is_file():
            logger.error(f"Path is not a file: {image_file_path}")
            raise APIError(
                f"Path is not a valid file: {image_file_path}", status_code=400
            )

        if not file_type:
            logger.error("File type not provided")
            raise APIError("File type must be specified", status_code=400)

        # Check if file type is supported
        if file_type not in ALLOWED_IMAGE_TYPES:
            logger.error(f"Unsupported image type: {file_type}")
            raise APIError(
                f"Unsupported image type: {file_type}. Supported types: JPEG, PNG, WebP, BMP, GIF, TIFF",
                status_code=400,
            )

        logger.info(f"Image type is supported: {file_type}")

        # ===== Step 1: Convert Image to PNG =====
        logger.info("Step 1: Converting image to PNG format")
        try:
            png_file_path = await convert_image_to_png(str(image_file_path), file_type)
            logger.info(f"Image successfully converted to PNG: {png_file_path}")
        except APIError as ae:
            logger.error(f"PNG conversion failed: {ae.message}")
            raise APIError(
                f"Failed to convert image to PNG: {ae.message}",
                status_code=ae.status_code,
                details=ae.details if hasattr(ae, "details") else None,
            )
        except Exception as e:
            logger.error(f"Unexpected error during PNG conversion: {str(e)}")
            raise APIError(
                "Failed to convert image to PNG", status_code=500, details=str(e)
            )

        # ===== Step 2: Load PNG Image =====
        logger.info("Step 2: Loading PNG image for OCR")
        try:
            logger.info(f"Loading PNG file: {png_file_path}")
            image = Image.open(str(png_file_path))
            logger.info(f"PNG image loaded. Size: {image.size}, Mode: {image.mode}")

        except FileNotFoundError as fnfe:
            logger.error(f"PNG file not found: {png_file_path}")
            raise APIError("PNG file not found", status_code=404, details=str(fnfe))
        except OSError as ose:
            logger.error(f"Invalid or corrupted PNG file: {str(ose)}")
            raise APIError(
                "Invalid or corrupted PNG file", status_code=400, details=str(ose)
            )
        except Exception as e:
            logger.error(f"Failed to load PNG image: {str(e)}")
            raise APIError("Failed to load PNG image", status_code=500, details=str(e))

        # ===== Step 3: Prepare Image for OCR =====
        logger.info("Step 3: Preparing PNG image for OCR processing")
        try:
            logger.info(f"Original image mode: {image.mode}")

            # Convert to RGB if necessary (Tesseract works best with RGB or Grayscale)
            if image.mode not in ("RGB", "L"):
                logger.info(f"Converting image mode from {image.mode} to RGB")
                image = image.convert("RGB")

            # Optional: Apply image enhancement for better OCR results
            # Uncomment if text extraction is poor
            # from PIL import ImageEnhance
            # enhancer = ImageEnhance.Contrast(image)
            # image = enhancer.enhance(2)

            logger.info("Image prepared for OCR")

        except Exception as e:
            logger.error(f"Failed to prepare image for OCR: {str(e)}")
            raise APIError(
                "Failed to prepare image for OCR", status_code=500, details=str(e)
            )

        # ===== Step 4: Extract Text Using OCR =====
        logger.info("Step 4: Starting Tesseract OCR text extraction")
        try:
            logger.info("Running Tesseract OCR on PNG image")

            # Extract text using Tesseract
            extracted_text = pytesseract.image_to_string(image)

            if not extracted_text:
                logger.warning(f"No text detected in image: {png_file_path}")
                raise APIError("No text detected in image", status_code=400)

            extracted_text = extracted_text.strip()

            if not extracted_text:
                logger.warning(
                    f"Extracted text is empty after stripping: {png_file_path}"
                )
                raise APIError("No readable text found in image", status_code=400)

            logger.info(
                f"Text extraction successful. Text length: {len(extracted_text)} characters"
            )

        except pytesseract.TesseractNotFoundError:
            logger.error("Tesseract OCR engine not found - please install Tesseract")
            raise APIError(
                "Tesseract OCR engine is not installed on the system",
                status_code=500,
                details="Please install Tesseract OCR to enable image text extraction",
            )
        except APIError:
            raise
        except Exception as e:
            logger.error(f"OCR extraction error: {str(e)}")
            raise APIError(
                "Failed to extract text from image", status_code=500, details=str(e)
            )

        # ===== Step 5: Delete PNG File =====
        logger.info("Step 5: Deleting PNG file after extraction")
        try:
            logger.info(f"Deleting PNG file: {png_file_path}")
            delete_file(str(png_file_path))
            logger.info(f"PNG file deleted successfully: {png_file_path}")
        except APIError as de:
            # Log warning but don't fail - extraction succeeded
            logger.warning(f"Failed to delete PNG file: {de.message}")
        except Exception as e:
            logger.warning(f"Unexpected error deleting PNG file: {str(e)}")

        logger.info("Text extraction completed successfully")
        return extracted_text

    except APIError:
        raise

    except Exception as e:
        logger.exception(f"Unexpected error during text extraction: {str(e)}")
        raise APIError(
            "Unexpected error during text extraction", status_code=500, details=str(e)
        )
