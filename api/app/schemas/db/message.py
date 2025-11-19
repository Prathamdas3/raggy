from pydantic import BaseModel, field_validator
from uuid import UUID
from typing import Optional
from datetime import datetime


class MessageResponse(BaseModel):
    id: UUID
    chat_id: UUID
    user_id: UUID
    question_id: Optional[UUID]
    sender: str
    content: str
    audio_url: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CreateMessage(BaseModel):
    user_id: UUID
    chat_id: UUID
    question_id: Optional[UUID] = None
    content: str

    @field_validator("user_id", "chat_id", mode="before")
    def check_fields(cls, v, info):
        if v is None:
            raise ValueError(f"{info.field_name} can not be empty")

        try:
            return UUID(str(v))
        except Exception:
            raise ValueError(f"{info.field_name} should be an UUID type")

    @field_validator("question_id", mode="before")
    def check_question_id(cls, v, info):
        if not v:
            return v

        if not isinstance(v, str):
            raise TypeError(f"{info.field_name} should be UUID")

        return v

    @field_validator("content", mode="before")
    def check_content(cls, v, info):
        if not v or not isinstance(v, str):
            raise TypeError(f"{info.field_name} should be string")

        v = v.strip()

        if not v:
            raise ValueError(f"{info.field_name} must not be empty")

        return v


class UpdateMessage(BaseModel):
    user_id: UUID
    chat_id: UUID
    question_id: UUID
    audio_url: str
    content: str

    class Config:
        exclude_unset = True

    @field_validator("user_id", "chat_id", "question_id", mode="before")
    def check_ids(cls, v, info):
        if not v:
            raise ValueError(f"{info.field_name} can not be empty")

        try:
            return UUID(str(v))
        except Exception:
            raise ValueError(f"{info.field_name} should be a valid uuid")

    @field_validator("audio_url", "content", mode="before")
    def check_audio_url(cls, v, info):
        if not v and not isinstance(v, str):
            raise TypeError(f"{info.field_name} should be string")

        v = v.strip()
        if not v:
            raise ValueError(f"{info.field_name} can not be empty")

        return v


class QueryInput(BaseModel):
    question: str

    @field_validator("question", mode="before")
    def check_question(cls, v, info):
        if not v or not isinstance(v, str):
            raise TypeError(f"{info.field_name} should be type of string")

        v = v.strip()

        if not v:
            raise ValueError(f"{info.field_name} can not be empty")

        return v


class GetAnswer(BaseModel):
    user_id: UUID
    chat_id: UUID
    question_id: UUID

    @field_validator("user_id", "chat_id", "question_id", mode="before")
    def check_id(cls, v, info):
        if not v:
            raise ValueError(f"{info.field_name} should not be empty")

        try:
            return UUID(str(v))
        except Exception:
            raise ValueError(f"{info.field_name} should be a valid UUID")
