from pydantic import BaseModel, field_validator
from typing import Optional
from uuid import UUID


class UpdateChat(BaseModel):
    chat_name: Optional[str] = None
    is_bookmarked: Optional[bool] = None

    class Config:
        exclude_unset = True

    @field_validator("chat_name", mode="before")
    def verify_chat_name(cls, v, field):
        if v is None:
            return v

        if not isinstance(v, str):
            raise TypeError(f"{field.name} should be type of string")

        if not v.strip():
            raise ValueError(f"{field.name} can not be empty")

        return v.strip()

    @field_validator("is_bookmarked", mode="before")
    def verify_is_bookmarked(cls, v, info):
        if v is None:
            return v

        if not isinstance(v, bool):
            raise TypeError(f"{info.field_name} should be type of boolean")

        return v

    def has_updates(self) -> bool:
        """Check if any fields were provided for update"""
        return any(v is not None for v in self.model_dump(exclude_unset=True).values())


class GetSummary(BaseModel):
    user_id: UUID
    chat_id: UUID

    @field_validator("chat_id", "user_id", mode="before")
    def check_ids(cls, v, info):
        if not v:
            raise ValueError(f"{info.field_name} can not be empty")

        try:
            return UUID(str(v))
        except Exception:
            raise ValueError(f"{info.field_name} should be a valid uuid")
