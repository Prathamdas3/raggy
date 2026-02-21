from typing import Optional
from app.core.pydantic import CustomBaseModel
from pydantic import EmailStr, field_validator
import re


class UpdateUser(CustomBaseModel):
    user_name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None

    class Config:
        exclude_unset = True

    @field_validator("first_name", "last_name", "user_name", mode="before")
    @classmethod
    def verify_details(cls, v, info):
        if v is None:
            return v  # null is allowed

        if not isinstance(v, str):
            raise TypeError(f"{info.field_name} should be type of string")

        if not v.strip():
            raise ValueError(f"{info.field_name} can not be empty")

        return v.strip()

    def has_updates(self) -> bool:
        """Check if any fields were provided for update"""
        return any(v is not None for v in self.model_dump(exclude_unset=True).values())


class CreateUser(CustomBaseModel):
    email: EmailStr
    password: str

    @field_validator("email", "password", mode="before")
    def verify_fields(cls, v, info):
        if not isinstance(v, str):
            raise TypeError(f"{info.field_name} must be a string")

        if not v.strip():
            raise ValueError(f"{info.field_name} cannot be empty or whitespace")

        return v.strip()

    @field_validator("password")
    def validate_password(cls, v):
        if not isinstance(v, str):
            raise TypeError("Password must be a string")

        v = v.strip()

        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one number")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Password must contain at least one special character")

        return v
