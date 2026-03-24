from uuid import UUID
from app.core import CustomBaseModel
from pydantic import field_validator

class UpdateSummary(CustomBaseModel):
    audio_url:str|None=None
    content:str|None=None
    summary_id:str
    
    @field_validator("summary_id")
    @classmethod
    def check_summary_id(cls,v:str)->UUID:
        try:
            return UUID(v)
        except Exception:
            raise TypeError("Summary Id must be of type UUID")
    
    
    def has_update(self) -> bool:
        """Check if any fields were provided for update."""
        return any(v is not None for v in self.model_dump(exclude_unset=True).values())
