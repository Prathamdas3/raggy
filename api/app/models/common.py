from app.core import CustomBaseModel
from enum import Enum
from typing import TypeVar, Generic, Optional

T = TypeVar("T")


class Status(Enum):
    success = "success"
    failed = "failed"


class Response(CustomBaseModel, Generic[T]):
    status: Status
    message: str
    data: Optional[T] = None
    error: Optional[T] = None

    model_config = {"use_enum_values": True}
