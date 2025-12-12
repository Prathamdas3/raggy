from fastapi import APIRouter, HTTPException, Path, Depends, status
from fastapi.responses import StreamingResponse
from app.configs.minio import get_file_stream, get_file_metadata
from app.services.auth.token import get_user_id_from_access_token
from app.utils.logger import get_logger
from minio.error import S3Error

logger = get_logger(__name__)
router = APIRouter(prefix="/api/v1/files", tags=["files"])


@router.get("/{bucket_name}/{file_path:path}")
async def download_file(
    bucket_name: str = Path(..., description="Name of the MinIO bucket"),
    file_path: str = Path(..., description="Path to the file in the bucket"),
    user_id: str = Depends(get_user_id_from_access_token),
):
    """
    Proxy file download from MinIO.
    Example: GET /api/v1/files/audio-files/audio/xxx/audio.mp3
    """
    if not user_id:
        HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No user found")

    try:
        logger.info(f"Proxying file: {bucket_name}/{file_path}")

        # Get file metadata for content type
        try:
            metadata = get_file_metadata(file_path, bucket_name)
            content_type = metadata.get("content_type", "application/octet-stream")
            file_size = metadata.get("size", 0)
        except S3Error:
            content_type = "application/octet-stream"
            file_size = None

        # Determine content type from extension if needed
        if content_type == "application/octet-stream":
            if file_path.endswith(".mp3"):
                content_type = "audio/mpeg"
            elif file_path.endswith(".pdf"):
                content_type = "application/pdf"
            elif file_path.endswith((".jpg", ".jpeg")):
                content_type = "image/jpeg"
            elif file_path.endswith(".png"):
                content_type = "image/png"

        # Get file stream
        file_stream = get_file_stream(file_path, bucket_name)

        # Build headers
        filename = file_path.split("/")[-1]
        headers = {
            "Content-Disposition": f'inline; filename="{filename}"',
            "Cache-Control": "public, max-age=3600",
        }

        if file_size:
            headers["Content-Length"] = str(file_size)

        logger.info(f"Streaming file: {filename} ({content_type})")

        return StreamingResponse(
            file_stream,
            media_type=content_type,
            headers=headers,
        )

    except S3Error as e:
        logger.error(f"MinIO error: {str(e)}")
        if e.code == "NoSuchKey":
            raise HTTPException(status_code=404, detail="File not found")
        raise HTTPException(status_code=500, detail="Error accessing file")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
