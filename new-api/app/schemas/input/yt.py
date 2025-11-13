from pydantic import BaseModel, field_validator
from uuid import UUID
from app.constants import YT_REGEX
from typing import Optional
from enum import Enum


class Type(Enum):
    yt = "yt"


class YTInput(BaseModel):
    user_id: UUID
    chat_id: UUID
    link: str
    input_type:Type

    @field_validator("link", mode="before")
    def check_link(cls, v, info):
        if not v or not isinstance(v, str):
            raise TypeError(f"{info.field_name} must be a string")

        v = v.strip()

        if not v:
            raise ValueError(f"{info.field_name} must be not be empty")

        if not YT_REGEX.match(v):
            raise ValueError("Invalid data format")

        return v

    @field_validator("user_id", "chat_id", mode="before")
    def verify_input(cls, v, info):
        if v is None:
            raise ValueError(f"{info.field_name} cannot be empty")
        try:
            return UUID(str(v))
        except Exception:
            raise ValueError(f"{info.field_name} must be a valid UUID")


class TaskInput(BaseModel):
    user_id: UUID
    chat_id: UUID
    text: str

    @field_validator("text", mode="before")
    def check_text(cls, v, info):
        if not v or not isinstance(v, str):
            raise TypeError(f"{info.field_name} must be string")

        v = v.strip()

        if not v:
            raise ValueError(f"{info.field_name} must be not be empty")

        return v

    @field_validator("user_id", "chat_id", mode="before")
    def verify_ids(cls, v, info):
        if v is None:
            raise ValueError(f"{info.field_name} can not be empty")

        try:
            return UUID(str(v))
        except Exception:
            raise ValueError(f"{info.field_name} must be a valid UUID")


class SpechInput(BaseModel):
    user_id: UUID
    chat_id: UUID
    summary_text: str
    question_id: Optional[UUID]

    @field_validator("summary_text", mode="before")
    def check_text(cls, v, info):
        if not v or not isinstance(v, str):
            raise TypeError(f"{info.field_name} must be string")

        v = v.strip()

        if not v:
            raise ValueError(f"{info.field_name} must be not be empty")

        return v

    @field_validator("user_id", "chat_id", mode="before")
    def verify_ids(cls, v, info):
        if v is None:
            raise ValueError(f"{info.field_name} can not be empty")

        try:
            return UUID(str(v))
        except Exception:
            raise ValueError(f"{info.field_name} must be a valid UUID")

    @field_validator("question_id", mode="before")
    def check_question_id(cls, v, info):
        if v is None:
            return v

        try:
            return UUID(str(v))
        except Exception:
            raise ValueError(f"{info.field_name} must be a valid UUID")
