from pathlib import Path
from typing import Union
from utils.response import APIError
from lib.logger import get_logger
import os
logger = get_logger("utils/files/delete")


async def delete_file(file_path: Union[str, Path]) -> None:
    """
    Delete a file from the given file path with comprehensive error handling.
    Raises APIError exceptions for different failure scenarios.
    
    Args:
        file_path: Path to the file to delete (string or Path object)
        
    Raises:
        APIError: With appropriate status codes:
            - 400: Empty path, path is directory, or invalid format
            - 403: Permission denied
            - 404: File doesn't exist
            - 500: OS or unexpected errors
    """
    # Convert to Path object for easier handling
    file_path = Path(file_path)
    
    logger.info(f"Attempting to delete file: {file_path}")
    
    try:
        # Check if the path is provided and valid format
        if not file_path:
            logger.error("Empty file path provided")
            raise APIError("File path cannot be empty", status_code=400)
        
        # Check if the path exists
        if not file_path.exists():
            logger.warning(f"File does not exist: {file_path}")
            raise APIError(f"File does not exist: {file_path}", status_code=404)
        
        # Check if it's actually a file (not a directory)
        if not file_path.is_file():
            logger.error(f"Path is not a file: {file_path}")
            raise APIError(
                f"Path is a directory, not a file: {file_path}",
                status_code=400
            )
        
        # Check if we have permission to delete
        if not os.access(file_path.parent, os.W_OK):
            logger.error(f"No write permission to delete file: {file_path}")
            raise APIError(
                "No permission to delete file (permission denied)",
                status_code=403
            )
        
        # Attempt to delete the file
        file_path.unlink()
        
        logger.info(f"File deleted successfully: {file_path}")
    
    except APIError:
        # Re-raise APIError as-is
        raise
    
    except PermissionError as pe:
        logger.error(f"Permission denied when deleting file: {file_path}: {str(pe)}")
        raise APIError(
            "Permission denied - unable to delete file",
            status_code=403,
            details=str(pe)
        )
    
    except IsADirectoryError as ide:
        logger.error(f"Attempted to delete a directory as file: {file_path}: {str(ide)}")
        raise APIError(
            "Cannot delete - path is a directory",
            status_code=400,
            details=str(ide)
        )
    
    except FileNotFoundError as fnfe:
        logger.warning(f"File not found during deletion: {file_path}: {str(fnfe)}")
        raise APIError(
            "File not found during deletion (may have been deleted by another process)",
            status_code=404,
            details=str(fnfe)
        )
    
    except OSError as ose:
        # Catch other OS-level errors (device busy, read-only filesystem, etc.)
        logger.error(f"OS error deleting file: {file_path}: {str(ose)}")
        raise APIError(
            "OS error - unable to delete file",
            status_code=500,
            details=str(ose)
        )
    
    except Exception as e:
        # Catch any unexpected errors
        logger.exception(f"Unexpected error deleting file: {file_path}")
        raise APIError(
            "Unexpected server error during file deletion",
            status_code=500,
            details=str(e)
        )

