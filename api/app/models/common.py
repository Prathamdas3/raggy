"""Common Pydantic models used across the application.

Contains shared models like Status enum and generic Response wrapper.
"""

from app.core import CustomBaseModel
from enum import Enum
from typing import TypeVar, Generic, Optional

T = TypeVar("T")


class Status(Enum):
    """Response status enumeration.

    Attributes:
        success: Operation was successful.
        failed: Operation failed.
    """

    success = "success"
    failed = "failed"


class Response(CustomBaseModel, Generic[T]):
    """Generic response model for API endpoints.

    Attributes:
        status: Response status (success or failed).
        message: Human-readable message.
        data: Optional response data payload.
        error: Optional error details.
    """

    status: Status
    message: str
    data: Optional[T] = None
    error: Optional[T] = None

    model_config = {"use_enum_values": True}
