from pydantic import BaseModel, field_validator,Field
from uuid import UUID


class SplitTextArgs(BaseModel):
    text: str
    chat_id: UUID
    user_id: UUID

    @field_validator("text", mode="before")
    def check_text(cls, v, info):
        if not v or not isinstance(v, str):
            raise TypeError(f"{info.field_name} must be a string")

        v = v.strip()

        if not v:
            raise ValueError(f"{info.field_name} can not be empty")

        return v

    @field_validator("user_id", "chat_id", mode="before")
    def check_id(cls, v, info):
        if not v:
            raise ValueError(f"{info.field_name} can not be empty")

        try:
            UUID(str(v))
        except Exception:
            raise ValueError(f"{info.field_name} must be a valid UUID type")


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
