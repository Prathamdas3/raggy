"""Common Pydantic models used across the application.

Contains shared models like Status enum and generic Response wrapper.
"""

from app.core import CustomBaseModel
from typing import TypeVar, Generic, Optional

T = TypeVar("T")


class Response(CustomBaseModel, Generic[T]):
    """Generic response model for API endpoints.

    Attributes:
        status: Response status (success or failed).
        message: Human-readable message.
        data: Optional response data payload.
        error: Optional error details.
    """

    data: Optional[T] = None
    error: Optional[T] = None

    model_config = {"use_enum_values": True}
