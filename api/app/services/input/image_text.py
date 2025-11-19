from app.utils.logger import get_logger
from pathlib import Path
from app.utils.remove_file import remove_file
from PIL import Image, ImageEnhance
from app.services.input.images_to_png import convert_to_png
import pytesseract

logger = get_logger(__name__)


def png_to_text(path: Path) -> str:
    file_path = Path(path)
    if not file_path:
        raise ValueError("Empty file path provided")

    if not file_path.exists():
        raise FileNotFoundError(f"File does not exist: {file_path}")

    if not file_path.is_file():
        raise IsADirectoryError(f"Path is not a file: {file_path}")

    try:
        png_file_path = convert_to_png(path=path)
        if not png_file_path:
            raise ValueError("No png image path found")
    except Exception:
        raise

    try:
        image = Image.open(str(png_file_path))
    except FileNotFoundError as fe:
        logger.error(
            f"Png file not found: {png_file_path}, error: {str(fe)}", exc_info=True
        )
        raise
    except OSError as oe:
        logger.error(f"Invalid or corrupted PNG file: {str(oe)}")
        raise RuntimeError("Invalid or corrupted PNG file")
    except Exception as e:
        logger.error(f"Failed to load PNG image: {str(e)}")
        raise

    try:
        logger.info(f"Original image mode: {image.mode}")

        # Convert to RGB if necessary (Tesseract works best with RGB or Grayscale)
        if image.mode not in ("RGB", "L"):
            logger.warning(f"Converting image mode from {image.mode} to RGB")
            image = image.convert("RGB")

        # Optional: Apply image enhancement for better OCR results
        # Uncomment if text extraction is poor
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2)
    except Exception as e:
        logger.error(f"Failed to prepare image for OCR: {str(e)}")
        raise

    try:
        logger.info("Running Tesseract OCR text extraction")
        extracted_text = pytesseract.image_to_string(image)
        if not extracted_text or not extracted_text.strip():
            logger.warning(f"No text detected in image: {png_file_path}")
            raise ValueError("No text found after extraction")

    except pytesseract.TesseractNotFoundError:
        logger.error("Tesseract OCR engine not found - please install Tesseract")
        raise

    except Exception as e:
        logger.error(f"Failed to prepare image for OCR: {str(e)}", exc_info=True)
        raise

    try:
        remove_file(png_file_path)
    except Exception as e:
        # Non-fatal — WAV is already created
        logger.warning(f"Could not delete original file: {e}")

    return extracted_text
