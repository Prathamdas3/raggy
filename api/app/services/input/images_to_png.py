from pathlib import Path
from app.utils.remove_file import remove_file
from app.utils.logger import get_logger
from PIL import Image

logger = get_logger(__name__)


def convert_to_png(path: Path) -> Path:
    file_path = Path(path)
    png_name = f"{file_path.stem}_converted.png"
    png_file_path = file_path.parent / png_name

    try:
        logger.info("Starting to convert the image to png")

        image = Image.open(str(file_path))
        logger.debug(f"Image loaded. Size: {image.size}, Mode: {image.mode}")

        # Convert RGBA images (with alpha channel) appropriately
        if image.mode in ("RGBA", "LA", "P"):
            logger.debug(
                f"Converting image mode from {image.mode} to RGBA for transparency support"
            )
            # Create white background
            background = Image.new("RGBA", image.size, (255, 255, 255, 255))
            if image.mode == "P":
                image = image.convert("RGBA")
            background.paste(
                image, mask=image.split()[-1] if image.mode == "RGBA" else None
            )
            image = background
        elif image.mode not in ("RGB", "RGBA"):
            logger.info(f"Converting image mode from {image.mode} to RGB")
            image = image.convert("RGB")

        # Save as PNG

        image.save(str(png_file_path), "PNG", quality=95, optimize=True)
        logger.info(f"Image successfully converted and saved to PNG: {png_file_path}")
    except FileNotFoundError as fe:
        logger.error(
            f"Image file not found during conversion: {str(fe)}", exc_info=True
        )
        raise ValueError("No Image file found during conversion")
    except OSError as oe:
        logger.error(
            f"Invalid or corrupted image file: {file_path} error: {str(oe)}",
            exc_info=True,
        )
        raise RuntimeError("Corrupted file found")
    except Exception as e:
        logger.error(f"Image conversion error: {str(e)}")

        # Clean up PNG file if conversion failed
        if png_file_path and png_file_path.exists():
            try:
                remove_file(png_file_path)
                logger.info(f"Cleaned up failed PNG file: {png_file_path}")
            except Exception as cleanup_e:
                logger.error(f"Failed to cleanup PNG file: {str(cleanup_e)}")

        raise Exception("Failed to convert image to PNG format")

    if not png_file_path.exists() or png_file_path.stat().st_size == 0:
        logger.error(f"PNG file was not created: {png_file_path}")
        raise Exception("PNG file was not created ")

    try:
        remove_file(file_path)
    except Exception as e:
        # Non-fatal — WAV is already created
        logger.warning(f"Could not delete original file: {e}")

    return png_file_path
