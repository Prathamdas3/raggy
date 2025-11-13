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

    @field_validator("user_id", "chat_id", mode="before")
    def check_user_data(cls, v, info):
        if v is None:
            raise ValueError(f"{info.field_name} cannot be empty")
        try:
            return UUID(str(v))
        except ValueError:
            raise ValueError(f"{info.field_name} must be a valid UUID")


class UpdateDocsData(BaseModel):
    user_id: UUID
    chat_id: UUID
    summary_text: Optional[str] = None
    audio_url: Optional[str] = None
    question_id: Optional[UUID] = None

    class Config:
        exclude_unset = True

    @field_validator("user_id", "chat_id", mode="before")
    def check_fields(cls, v, info):
        if v is None:
            raise ValueError(f"{info.field_name} cannot be empty")
        try:
            return UUID(str(v))
        except ValueError:
            raise ValueError(f"{info.field_name} must be a valid UUID")

    @field_validator("summary_text", "audio_url", mode="before")
    def check_details(cls, v, info):
        if not v:
            return v

        if not isinstance(v, str):
            raise TypeError(f"{info.field_name} must be string")

        return v

    @field_validator("question_id", mode="before")
    def check_question_id(cls, v, info):
        if not v:
            return v

        try:
            UUID(str(v))
        except Exception:
            raise ValueError(f"{info.field_name} should be a valid UUID")

    def has_updates(self) -> bool:
        return any(v is not None for v in self.model_dump(exclude_unset=True).values())
