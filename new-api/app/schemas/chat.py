from pydantic import BaseModel, field_validator
from typing import Optional


class UpdateChat(BaseModel):
    chat_name: Optional[str] = None
    is_bookmarked: Optional[bool] = None

    class Config:
        exclude_unset = True

    @field_validator("chat_name", mode="before")
    def verify_chat_name(cls, v, field):
        if not v:
            return v

        if not isinstance(v, str):
            raise TypeError(f"{field.name} should be type of string")

        if not v.strip():
            raise ValueError(f"{field.name} can not be empty")

        return v.strip()

    @field_validator("is_bookmarked", mode="before")
    def verify_is_bookmarked(cls, v, field):
        if not v:
            return v

        if not isinstance(v, str):
            raise TypeError(f"{field.name} should be type of string")

        return v.strip()

    def has_updates(self) -> bool:
        """Check if any fields were provided for update"""
        return any(v is not None for v in self.model_dump(exclude_unset=True).values())
