from pydantic import BaseModel
from datetime import datetime


class CustomBaseModel(BaseModel):
    class Config:
        populate_by_name = True
        json_encoders = {datetime: datetime.isoformat}
