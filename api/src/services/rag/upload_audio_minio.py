from lib.celery import celery
from lib.logger import get_logger
from lib.minio import get_minio_client, get_bucket_name
from minio.error import S3Error
from pathlib import Path
from datetime import timedelta
from utils.delete import delete_file
import asyncio


logger = get_logger("workers/upload_audio_minio")


@celery.task(bind=True, max_retries=3)
def upload_audio_to_minio(self, temp_file_path: str, chat_id: str):
    """
    Upload audio file to MinIO bucket, delete temp file after successful upload,
    and store the audio URL in the database.

    Args:
        temp_file_path: Path to the temporary audio file
        chat_id: The chat ID for organizing audio files
        user_id: The user ID for database storage

    Returns:
        dict: Contains success status, MinIO path/URL, and any error messages
    """
    temp_path = None
    minio_object_name = None
    upload_successful = False

    try:
        logger.info(
            f"Starting MinIO upload for chat_id: {chat_id}, file: {temp_file_path}"
        )

        # Get MinIO client instance (singleton)
        try:
            minio_client = get_minio_client()
            bucket_name = get_bucket_name()
        except Exception as client_error:
            logger.error(f"Failed to get MinIO client: {str(client_error)}")
            return {
                "success": False,
                "error": f"MinIO client error: {str(client_error)}",
                "minio_path": None,
                "minio_url": None,
            }

        # Validate inputs
        if not temp_file_path or not isinstance(temp_file_path, str):
            logger.error("Invalid temp_file_path provided")
            return {
                "success": False,
                "error": "Invalid temp file path provided",
                "minio_path": None,
                "minio_url": None,
            }

        if not chat_id or not isinstance(chat_id, str):
            logger.error("Invalid chat_id provided")
            return {
                "success": False,
                "error": "Invalid chat_id provided",
                "minio_path": None,
                "minio_url": None,
            }

        # Convert to Path object and validate
        temp_path = Path(temp_file_path)

        if not temp_path.exists():
            logger.error(f"Temp file does not exist: {temp_file_path}")
            return {
                "success": False,
                "error": f"Temp file does not exist: {temp_file_path}",
                "minio_path": None,
                "minio_url": None,
            }

        if not temp_path.is_file():
            logger.error(f"Path is not a file: {temp_file_path}")
            return {
                "success": False,
                "error": f"Path is not a file: {temp_file_path}",
                "minio_path": None,
                "minio_url": None,
            }

        # Get file size
        file_size = temp_path.stat().st_size
        if file_size == 0:
            logger.error(f"Temp file is empty: {temp_file_path}")
            return {
                "success": False,
                "error": "Temp file is empty",
                "minio_path": None,
                "minio_url": None,
            }

        logger.info(f"Temp file validated. Size: {file_size} bytes")

        # Create MinIO object name with chat_id structure
        file_name = temp_path.name
        minio_object_name = f"audio/{chat_id}/{file_name}"

        logger.info(f"Uploading file to MinIO: {minio_object_name}")

        # Upload file to MinIO
        try:
            result = minio_client.fput_object(
                bucket_name=bucket_name,
                object_name=minio_object_name,
                file_path=str(temp_path),
                content_type="audio/mpeg",
            )

            upload_successful = True
            logger.info(f"File uploaded successfully to MinIO: {minio_object_name}")
            logger.info(
                f"Upload result - ETag: {result.etag}, Version: {result.version_id}"
            )

        except S3Error as s3_error:
            logger.error(f"S3Error during upload: {str(s3_error)}")
            return {
                "success": False,
                "error": f"MinIO upload failed: {str(s3_error)}",
                "minio_path": None,
                "minio_url": None,
            }
        except Exception as upload_error:
            logger.error(f"Unexpected error during upload: {str(upload_error)}")
            return {
                "success": False,
                "error": f"Upload failed: {str(upload_error)}",
                "minio_path": None,
                "minio_url": None,
            }

        # Verify upload by checking object existence
        try:
            stat = minio_client.stat_object(bucket_name, minio_object_name)
            logger.info(f"Upload verified. Object size: {stat.size} bytes")

            if stat.size != file_size:
                logger.warning(
                    f"File size mismatch. Original: {file_size}, Uploaded: {stat.size}"
                )
        except S3Error as stat_error:
            logger.error(f"Failed to verify uploaded object: {str(stat_error)}")
            return {
                "success": False,
                "error": f"Upload verification failed: {str(stat_error)}",
                "minio_path": None,
                "minio_url": None,
            }

        # Generate presigned URL (valid for 7 days)
        try:
            minio_url = minio_client.presigned_get_object(
                bucket_name=bucket_name,
                object_name=minio_object_name,
                expires=timedelta(days=7),
            )
            logger.info(f"Generated presigned URL (truncated): {minio_url[:100]}...")
        except Exception as url_error:
            logger.warning(f"Failed to generate presigned URL: {str(url_error)}")
            # Create a basic URL without presigned access
            from lib.minio import MINIO_ENDPOINT, MINIO_SECURE

            protocol = "https" if MINIO_SECURE else "http"
            minio_url = (
                f"{protocol}://{MINIO_ENDPOINT}/{bucket_name}/{minio_object_name}"
            )

        # Delete temp file after successful upload
        logger.info(f"Attempting to delete temp file: {temp_file_path}")
        try:
            # Use asyncio to run the async delete_file function
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(delete_file(temp_path))
            loop.close()
            logger.info(f"Temp file deleted successfully: {temp_file_path}")
        except Exception as delete_error:
            logger.error(f"Failed to delete temp file: {str(delete_error)}")
            # Don't fail the task if deletion fails, just log it
            logger.warning("Continuing despite temp file deletion failure")

        logger.info(f"MinIO upload completed successfully for chat_id: {chat_id}")

        # ===== Call store_audio_to_db task to save audio URL in database =====
        logger.info(f"Triggering store_audio_to_db task for chat_id: {chat_id}")
        try:
            from workers.db.store_audio import store_audio_to_db

            # Call the task asynchronously
            db_task_result = store_audio_to_db.delay(
                chat_id=chat_id, audio_url=minio_url
            )

            logger.info(
                f"store_audio_to_db task triggered successfully. Task ID: {db_task_result.id}"
            )

            # Optionally, you can wait for the result (blocking)
            # db_result = db_task_result.get(timeout=30)
            # logger.info(f"Database storage result: {db_result}")

        except Exception as db_task_error:
            logger.error(
                f"Failed to trigger store_audio_to_db task: {str(db_task_error)}"
            )
            # Don't fail the main task, just log the error
            logger.warning(
                "MinIO upload succeeded, but database storage task failed to trigger"
            )

        return {
            "success": True,
            "error": None,
            "minio_path": minio_object_name,
            "minio_url": minio_url,
            "bucket_name": bucket_name,
            "file_size": file_size,
            "db_task_triggered": True,
        }

    except Exception as e:
        logger.exception(f"Unexpected error in upload_audio_to_minio: {str(e)}")

        # If upload failed and temp file still exists, keep it for retry
        if not upload_successful and temp_path and temp_path.exists():
            logger.info(f"Keeping temp file for potential retry: {temp_file_path}")

        # Retry the task if we haven't exceeded max retries
        if self.request.retries < self.max_retries:
            logger.info(
                f"Retrying task. Attempt {self.request.retries + 1}/{self.max_retries}"
            )
            raise self.retry(exc=e, countdown=60)  # Retry after 60 seconds

        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "minio_path": None,
            "minio_url": None,
            "db_task_triggered": False,
        }
