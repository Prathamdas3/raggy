from typing import  Generic, TypeVar,Optional
from enum import Enum
from pydantic import BaseModel

T=TypeVar("T")

class Status(Enum):
    success= "success",
    error="error"


class Response(BaseModel,Generic[T]):
    status:Status
    message:str
    data:Optional[T]=None
    error:Optional[str]=None