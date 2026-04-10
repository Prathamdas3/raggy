"""Chat-related Pydantic models.

Contains request/response models for chat updates and file extraction.
"""

from app.core import CustomBaseModel
from app.schemas import Status

from pydantic import field_validator, model_validator
from typing import Optional
from uuid import UUID


class UpdateChat(CustomBaseModel):
    """Model for updating chat metadata.

    Attributes:
        title: Optional new title for the chat.
        original_text: Optional original text content.
        processing_status: Optional processing status.
        is_bookmarked: Optional bookmark flag.
        share_id: Optional share identifier.
    """
    chat_id:UUID
    user_id:UUID
    title: Optional[str] = None
    shared_doc: Optional[str] = None
    processing_status: Optional[Status] = None
    is_bookmarked: Optional[bool] = None
    share_id: Optional[str] = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, v):
        """Validate title is not blank and within length limit."""
        if v is not None and len(v.strip()) == 0:
            raise ValueError("Title cannot be blank")
        if v is not None and len(v) > 255:
            raise ValueError("Title must be 255 characters or less")
        return v.strip() if v else v

    @field_validator("shared_doc")
    @classmethod
    def validate_original_text(cls, v):
        """Validate original text is not blank."""
        if v is not None and len(v.strip()) == 0:
            raise ValueError("Shared doc cannot be blank")
        return v.strip() if v else v

    @field_validator("share_id")
    @classmethod
    def validate_share_id(cls, v):
        """Validate share ID is not blank."""
        if v is not None and len(v.strip()) == 0:
            raise ValueError("Share ID cannot be blank")
        return v.strip() if v else v

    @model_validator(mode="after")
    def validate_has_at_least_one_field(self):
        """Ensure at least one field is provided for update."""
        if not self.has_update():
            raise ValueError("At least one field must be provided to update")
        return self

    def has_update(self) -> bool:
        """Check if any fields were provided for update."""
        return any(v is not None for v in self.model_dump(exclude_unset=True).values())
