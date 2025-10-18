from pathlib import Path
from constants import ALLOWED_IMAGE_TYPES
from utils.response import APIError
from utils.files.delete import delete_file
from lib.logger import get_logger
import os
from PIL import Image
logger=get_logger("utils/converters/images_to_png")

async def convert_image_to_png(file_path: str, file_type: str) -> str:
    """
    Convert image files to PNG format.
    
    Supports:
    - JPEG, JPG, PNG, WebP, BMP, GIF, TIFF, ICO
    
    Args:
        file_path: Path to the image file
        file_type: MIME type of the image
        
    Returns:
        str: Path to the converted PNG image file
        
    Raises:
        APIError: With appropriate status codes for different failure scenarios:
            - 400: Invalid input, unsupported format
            - 404: File not found
            - 500: Conversion/IO errors
    """
    file_path = Path(file_path)
    png_file_path = None
    
    logger.info(f"Starting image conversion to PNG. File: {file_path}, Type: {file_type}")
    
    try:
        # ===== Input Validation =====
        if not file_path:
            logger.error("Empty file path provided")
            raise APIError("File path cannot be empty", status_code=400)
        
        if not file_path.exists():
            logger.error(f"Image file does not exist: {file_path}")
            raise APIError(f"Image file not found: {file_path}", status_code=404)
        
        if not file_path.is_file():
            logger.error(f"Path is not a file: {file_path}")
            raise APIError(f"Path is not a valid file: {file_path}", status_code=400)
        
        if not file_type:
            logger.error("File type not provided")
            raise APIError("File type must be specified", status_code=400)
        
        # Check if file type is supported
        if file_type not in ALLOWED_IMAGE_TYPES:
            logger.error(f"Unsupported image type: {file_type}")
            raise APIError(
                f"Unsupported image type: {file_type}. Supported types: JPEG, PNG, WebP, BMP, GIF, TIFF, ICO",
                status_code=400
            )
        
        logger.info(f"Image type is supported: {file_type}")
        
        # ===== Create PNG File Path =====
        png_name = f"{file_path.stem}_converted.png"
        png_file_path = file_path.parent / png_name
        logger.info(f"PNG file will be saved to: {png_file_path}")
        
        # ===== Load and Convert Image =====
        try:
            logger.info(f"Loading image file: {file_path}")
            
            # Open the image
            image = Image.open(str(file_path))
            logger.info(f"Image loaded. Size: {image.size}, Mode: {image.mode}")
            
            # Convert RGBA images (with alpha channel) appropriately
            if image.mode in ("RGBA", "LA", "P"):
                logger.info(f"Converting image mode from {image.mode} to RGBA for transparency support")
                # Create white background
                background = Image.new("RGBA", image.size, (255, 255, 255, 255))
                if image.mode == "P":
                    image = image.convert("RGBA")
                background.paste(image, mask=image.split()[-1] if image.mode == "RGBA" else None)
                image = background
            elif image.mode not in ("RGB", "RGBA"):
                logger.info(f"Converting image mode from {image.mode} to RGB")
                image = image.convert("RGB")
            
            # Save as PNG
            logger.info(f"Saving image as PNG: {png_file_path}")
            image.save(str(png_file_path), "PNG", quality=95, optimize=True)
            logger.info(f"Image successfully converted and saved to PNG: {png_file_path}")
            
        except FileNotFoundError as fnfe:
            logger.error(f"Image file not found during conversion: {file_path}")
            raise APIError(
                "Image file not found during conversion",
                status_code=404,
                details=str(fnfe)
            )
        except OSError as ose:
            logger.error(f"Invalid or corrupted image file: {file_path}: {str(ose)}")
            raise APIError(
                "Invalid or corrupted image file",
                status_code=400,
                details=str(ose)
            )
        except Exception as e:
            logger.error(f"Image conversion error: {str(e)}")
            
            # Clean up PNG file if conversion failed
            if png_file_path and png_file_path.exists():
                try:
                    os.remove(png_file_path)
                    logger.info(f"Cleaned up failed PNG file: {png_file_path}")
                except Exception as cleanup_e:
                    logger.error(f"Failed to cleanup PNG file: {str(cleanup_e)}")
            
            raise APIError(
                "Failed to convert image to PNG format",
                status_code=500,
                details=str(e)
            )
        
        # ===== Verify PNG File =====
        if not png_file_path.exists():
            logger.error(f"PNG file was not created: {png_file_path}")
            raise APIError(
                "PNG file was not created successfully",
                status_code=500
            )
        
        file_size = png_file_path.stat().st_size
        
        if file_size == 0:
            logger.error(f"PNG file is empty: {png_file_path}")
            try:
                os.remove(png_file_path)
            except Exception as e:
                logger.error(f"Failed to cleanup empty PNG file: {str(e)}")
            
            raise APIError(
                "PNG file created but is empty",
                status_code=500
            )
        
        logger.info(f"PNG file verified. Size: {file_size / (1024*1024):.2f} MB")
        
        # ===== Delete Original File =====
        try:
            logger.info(f"Deleting original image file: {file_path}")
            await delete_file(str(file_path))
            logger.info(f"Original image file deleted successfully: {file_path}")
        except APIError as de:
            # Log warning but don't fail - PNG was created successfully
            logger.warning(f"Failed to delete original file: {de.message}")
        except Exception as e:
            logger.warning(f"Unexpected error deleting original file: {str(e)}")
        
        logger.info(f"Image conversion completed successfully. Output: {png_file_path}")
        return str(png_file_path)
    
    except APIError:
        raise
    
    except Exception as e:
        logger.exception(f"Unexpected error during image conversion: {str(e)}")
        
        # Clean up PNG file on unexpected error
        if png_file_path and png_file_path.exists():
            try:
                os.remove(png_file_path)
                logger.info(f"Cleaned up PNG file after error: {png_file_path}")
            except Exception as cleanup_e:
                logger.error(f"Failed to cleanup PNG file: {str(cleanup_e)}")
        
        raise APIError(
            "Unexpected error during image conversion",
            status_code=500,
            details=str(e)
        )