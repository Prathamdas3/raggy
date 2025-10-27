from typing import Generic, List, TypeVar, Optional, Any
from pydantic import BaseModel, Field, field_validator

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


class ChunkMetadata(BaseModel):
    """Metadata for each chunk"""

    user_id: str = Field(..., min_length=1, description="User ID")
    chat_id: str = Field(..., min_length=1, description="Chat ID")
    chunk_index: int = Field(..., ge=0, description="Chunk index (must be >= 0)")

    @field_validator("user_id", "chat_id")
    def validate_not_empty(cls, v, info):
        v = v.strip()
        if not v:
            raise ValueError(f"{info.field_name} cannot be empty or whitespace")
        return v


class ChunkData(BaseModel):
    """Individual chunk structure"""

    content: str = Field(..., min_length=1, description="Chunk content")
    metadata: ChunkMetadata

    @field_validator("content")
    def validate_content(cls, v):
        v = v.strip()
        if not v:
            raise ValueError("content cannot be empty or whitespace")
        return v


class SaveToQdrantRequest(BaseModel):
    """Request body for saving chunks to Qdrant"""

    chunks: List[ChunkData] = Field(
        ..., min_items=1, description="List of chunks to save"
    )

    @field_validator("chunks")
    def validate_chunks(cls, v):
        if not v:
            raise ValueError("chunks list cannot be empty")
        return v


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
