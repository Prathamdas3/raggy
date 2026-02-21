from pydantic import BaseModel, ConfigDict
from datetime import datetime


class CustomBaseModel(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True, json_encoders={datetime: datetime.isoformat}
    )
