from pydantic import BaseModel, model_validator, field_validator
from fastapi import UploadFile
from typing import Optional
from uuid import UUID


class DocsReq(BaseModel):
    file: Optional[UploadFile] = None
    link: Optional[str] = None

    @model_validator(mode="after")
    def check_deatils(self):
        if not self.file or not self.link:
            raise ValueError(
                "file or link should be provided,req data can not be empty"
            )

        if self.file and self.link:
            self.link = None

        return self


class CreateText(BaseModel):
    user_id: UUID
    chat_id: UUID
    original_text: str

    @field_validator("original_text", mode="before")
    def check_text(cls, v, info):
        if not v or not isinstance(v, str):
            raise TypeError(f"{info.field_name} should be string")

        v = v.strip()

        if not v:
            raise ValueError(f"{info.field_name} can not be empty")

        return v
    
    @field_validator("user_id","chat_id",mode="before")
    def check_user_data(cls,v,info):
        if v is None:
            raise ValueError(f"{info.field_name} cannot be empty")
        try:
            return UUID(str(v))
        except ValueError:
            raise ValueError(f"{info.field_name} must be a valid UUID")
