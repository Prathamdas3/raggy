from uuid import UUID
from app.core.pydantic import CustomBaseModel
from pydantic import EmailStr, field_validator


class SigninUser(CustomBaseModel):
    email: EmailStr
    password: str

    @field_validator("email", "password", mode="before")
    def verify_fields(cls, v, info):
        if not isinstance(v, str):
            raise TypeError(f"{info.field_name} must be a string")

        if not v.strip():
            raise ValueError(f"{info.field_name} cannot be empty or whitespace")

        return v.strip()


class UpdatePassword(CustomBaseModel):
    user_id: UUID
    old_password: str
    new_password: str

    @field_validator("user_id", mode="before")
    def check_user_id(cls, v, info):
        if not v:
            raise ValueError(f"{info.field_name} no user_id found")

        try:
            return UUID(str(v))
        except Exception:
            raise ValueError(f"{info.field_name} should be a type of valid UUID")

    @field_validator("old_password", "new_password", mode="before")
    def check_passwords(cls, v, info):
        if not v or not isinstance(v, str):
            raise TypeError(f"{info.field_name} should be type of string")

        v = v.strip()
        if not v:
            raise ValueError(f"{info.field_name} can not be empty")

        return v


class UpdatePasswordInput(CustomBaseModel):
    old_password: str
    new_password: str

    @field_validator("old_password", "new_password", mode="before")
    def check_passwords(cls, v, info):
        if not v or not isinstance(v, str):
            raise TypeError(f"{info.field_name} should be type of string")

        v = v.strip()
        if not v:
            raise ValueError(f"{info.field_name} can not be empty")

        return v
