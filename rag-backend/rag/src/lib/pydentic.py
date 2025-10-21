from typing import Generic, List, TypeVar, Optional
from pydantic import BaseModel

T = TypeVar("T")


class SuccessResponse(BaseModel, Generic[T]):
    status: str = "success"
    message: Optional[str] = None
    data: Optional[T] = None


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


class QuestionRequest(BaseModel):
    """Request model for question answering"""

    user_id: str
    chat_id: str
    question: str


class SummaryRequest(BaseModel):
    """Request model for summary generation"""

    user_id: str
    chat_id: str
    original_text: str


class SummaryStore(BaseModel):
    """Response model for summary generation"""

    user_id: str
    chat_id: str
    summary: str
