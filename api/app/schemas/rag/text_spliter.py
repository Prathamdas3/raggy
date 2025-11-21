from pydantic import BaseModel, field_validator, Field

class ChunkMetadata(BaseModel):
    """Metadata for each chunk"""

    chunk_index: int = Field(..., ge=0, description="Chunk index (must be >= 0)")



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
