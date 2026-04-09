from uuid import UUID
from app.core import CustomBaseModel

class UpdateSummary(CustomBaseModel):
    audio_url:str|None=None
    content:str|None=None
    summary_id:UUID
        
    def has_update(self) -> bool:
        """Check if any fields were provided for update."""
        return any(v is not None for v in self.model_dump(exclude_unset=True).values())
