"""File-related Pydantic models.

Contains models for file metadata and type classification.
"""

from enum import Enum
from typing import Self
from app.core import CustomBaseModel
from fastapi import UploadFile
from app.constants import (
    ALLOWED_AUDIO_TYPES,
    ALLOWED_DOC_TYPES,
    ALLOWED_IMAGE_TYPES,
    ALLOWED_VIDEO_TYPES,
)
import os


class Type(Enum):
    """File type enumeration.

    Attributes:
        image: Image files (jpeg, png, etc.).
        audio: Audio files (mp3, wav, etc.).
        video: Video files (mp4, mov, etc.).
        document: Document files (pdf, docx, etc.).
    """

    image = "image"
    audio = "audio"
    video = "video"
    document = "document"


class FileMeta(CustomBaseModel):
    """File metadata model extracted from uploads.

    Attributes:
        filename: Original filename.
        content_type: MIME content type.
        extension: File extension without dot.
        category: File category (image, audio, video, document).
        subtype: Specific file subtype (e.g., pdf, mp3).
    """

    filename: str
    content_type: str
    extension: str
    category: str
    subtype: str

    @classmethod
    def from_upload(cls, file: UploadFile) -> Self:
        """Create FileMeta from an uploaded file.

        Args:
            file: FastAPI UploadFile object.

        Returns:
            FileMeta instance with extracted metadata.

        Raises:
            ValueError: If filename or content_type is missing,
                       or file type is not supported.
        """
        filename = file.filename
        if filename is None or not filename.strip():
            raise ValueError("No file name found")

        content_type = file.content_type
        if content_type is None or not content_type.strip():
            raise ValueError("No content type found")

        extension = os.path.splitext(filename)[1].replace(".", "").lower()

        # category detection
        if content_type in ALLOWED_IMAGE_TYPES:
            category = "image"
        elif content_type in ALLOWED_AUDIO_TYPES:
            category = "audio"
        elif content_type in ALLOWED_VIDEO_TYPES:
            category = "video"
        elif content_type in ALLOWED_DOC_TYPES:
            category = "document"
        else:
            raise ValueError(f"Unsupported file type: {content_type}")

        # subtype extraction: everything after "/"
        subtype = content_type.split("/")[-1]  # e.g. "jpeg", "mpeg", "pdf"

        return cls(
            filename=filename,
            content_type=content_type,
            extension=extension,
            category=category,
            subtype=subtype,
        )
