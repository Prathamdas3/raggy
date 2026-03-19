from pathlib import Path
from uuid import UUID
from app.core import CustomBaseModel
from app.db import Status

from pydantic import field_validator, model_validator
from typing import Optional


class UpdateChat(CustomBaseModel):
    title: Optional[str] = None
    original_text: Optional[str] = None
    processing_status: Optional[Status] = None
    is_bookmarked: Optional[bool] = None
    share_id: Optional[str] = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, v):
        if v is not None and len(v.strip()) == 0:
            raise ValueError("Title cannot be blank")
        if v is not None and len(v) > 255:
            raise ValueError("Title must be 255 characters or less")
        return v.strip() if v else v

    @field_validator("original_text")
    @classmethod
    def validate_original_text(cls, v):
        if v is not None and len(v.strip()) == 0:
            raise ValueError("Original text cannot be blank")
        return v.strip() if v else v

    @field_validator("share_id")
    @classmethod
    def validate_share_id(cls, v):
        if v is not None and len(v.strip()) == 0:
            raise ValueError("Share ID cannot be blank")
        return v.strip() if v else v

    @model_validator(mode="after")
    def validate_has_at_least_one_field(self):
        if not self.has_update():
            raise ValueError("At least one field must be provided to update")
        return self

    def has_update(self) -> bool:
        return any(v is not None for v in self.model_dump(exclude_unset=True).values())


class ExtractChat(CustomBaseModel):
    doc_id: str
    file_path: str
    file_type:str

    @field_validator("doc_id")
    def validate_doc_id(cls,v:str)->UUID:
        try:
            return UUID(v)
        except Exception:
            raise TypeError("Doc Id should be UUID")

    @field_validator("file_path")
    @classmethod
    def validate_file_path(cls, v:str) -> Path:
        try:
            v:Path=Path(v)
        except Exception:
            raise TypeError("Given string is not a path")
        v = v.resolve()
        if not v.exists():
            raise ValueError(f"File does not exist: {v}")
        if not v.is_file():
            raise ValueError(f"Path is not a file: {v}")
        return v