from pydantic import BaseModel, field_validator
from fastapi import UploadFile
from pathlib import Path
from uuid import UUID
from app.constants import (
    ALLOWED_AUDIO_TYPES,
    ALLOWED_DOC_TYPES,
    ALLOWED_IMAGE_TYPES,
    ALLOWED_VIDEO_TYPES,
)
import os
from enum import Enum


class Type(Enum):
    image = "image"
    audio_video = "audio_video"
    other="other"


class FileMeta(BaseModel):
    filename: str
    content_type: str
    extension: str
    category: str
    subtype: str  # <-- ACTUAL request fulfilled

    @classmethod
    def from_upload(cls, file: UploadFile):
        filename = file.filename
        content_type = file.content_type  # e.g. "image/jpeg"
        extension = os.path.splitext(filename)[1].replace(".", "").lower()

        # category detection
        if content_type in ALLOWED_IMAGE_TYPES:
            category = "image"
        elif content_type in (ALLOWED_AUDIO_TYPES | ALLOWED_VIDEO_TYPES):
            category = "audio_video"
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


class OtherInput(BaseModel):
    path: Path
    user_id: UUID
    chat_id: UUID
    type: Type

    @field_validator("path", mode="before")
    def validate_path(cls, v):
        if not v:
            raise ValueError("path cannot be empty")

        try:
            return Path(v)
        except Exception:
            raise ValueError("path must be a valid filesystem path string")

    @field_validator("user_id", "chat_id", mode="before")
    def validate_uuid(cls, v, info):
        if not v:
            raise ValueError(f"{info.field_name} cannot be empty")

        try:
            return UUID(str(v))
        except Exception:
            raise ValueError(f"{info.field_name} must be a valid UUID")
