from datetime import datetime, timedelta
import asyncio
from pathlib import Path
from utils.logger import get_logger

logger = get_logger("utils/files/clean")
TEMP_DIR = Path("temp")
TEMP_DIR.mkdir(exist_ok=True)
CLEANUP_INTERVAL = 60 * 60  # every 1 hour
FILE_TTL = timedelta(hours=1) 


async def cleanup_temp_files():
    """
    Background task to clean up temporary files older than FILE_TTL.
    Runs every CLEANUP_INTERVAL seconds.
    """
    logger.info("Starting cleanup_temp_files task")
    
    while True:
        try:
            now = datetime.now()
            
            if not TEMP_DIR.exists() or not TEMP_DIR.is_dir():
                logger.info("Temp directory does not exist or is not a directory")
                await asyncio.sleep(CLEANUP_INTERVAL)
                continue

            for file_path in TEMP_DIR.iterdir():
                try:
                    if file_path.is_file():
                        file_age = now - datetime.fromtimestamp(
                            file_path.stat().st_mtime
                        )
                        if file_age > FILE_TTL:
                            file_path.unlink()
                            logger.info(f"Deleted old temp file: {file_path.name}")  # Fixed
                
                except FileNotFoundError:
                    # File may have been deleted between iterdir() and stat()
                    continue
                
                except PermissionError as e:
                    logger.error(
                        f"Permission error deleting file {file_path.name}: {str(e)}"
                    )
                
                except Exception as e:
                    logger.error(
                        f"Unexpected error deleting file {file_path.name}: {str(e)}"
                    )

        except Exception as e:
            logger.error(f"Unexpected error in cleanup loop: {str(e)}")

        await asyncio.sleep(CLEANUP_INTERVAL)

