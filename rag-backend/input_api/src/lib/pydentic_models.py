from typing import Any, Generic, List, TypeVar, Optional
from pydantic import BaseModel

T = TypeVar("T")


class SuccessResponse(BaseModel, Generic[T]):
    status: str = "success"
    message: Optional[str] = None
    data: Optional[T] = None


class ErrorResponse(BaseModel):
    status: str = "error"
    message: str
    code: Optional[int] = None
    details: Optional[Any] = None


class YTRequestModel(BaseModel):
    link: str
    user_id: str
    chat_id: str


class ChunkMetadata(BaseModel):
    """Metadata for each chunk"""

    user_id: str
    chat_id: str
    chunk_index: int


class ChunkData(BaseModel):
    """Individual chunk structure"""

    content: str
    metadata: ChunkMetadata


class SendChunksRequest(BaseModel):
    """Request model to send chunks to docs API"""

    user_id: str
    chat_id: str
    original_text: List[ChunkData]
