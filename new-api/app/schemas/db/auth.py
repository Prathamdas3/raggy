from pydantic import BaseModel, field_validator, EmailStr
from datetime import datetime
from uuid import UUID


class SessionCreate(BaseModel):
    ip_address: str
    user_id: UUID
    expires_at: datetime
    user_agent: str
    token: str

    @field_validator("ip_address", "user_agent", "token", mode="before")
    def verify_data(cls, v, field):
        if not v or not isinstance(v, str):
            raise TypeError(f"{field.name} should be string")

        if not v.strip():
            raise ValueError(f"{field.name} should not be empty")

        return v.strip()

    @field_validator("user_id")
    def check_userid(cls, v, info):
        if v is None:
            raise ValueError(f"{info.field_name} cannot be empty")
        try:
            return UUID(str(v))
        except ValueError:
            raise ValueError(f"{info.field_name} must be a valid UUID")

    @field_validator("expires_at")
    def check_datetime(cls, v):
        if not isinstance(v, datetime):
            raise TypeError("expires_at must be a datetime")
        return v


class SignIn(BaseModel):
    email: EmailStr
    password: str

    @field_validator("email", "password", mode="before")
    def verify_email(cls, v, info):
        if not isinstance(v, str):
            raise TypeError(f"{info.field_name} must follow the email format")

        if not v.strip():
            raise ValueError(f"{info.field_name} should not be empty")

        return v.strip()

    @field_validator("password", mode="before")
    def verify_password(cls, v, info):
        if not v or not isinstance(v, str):
            raise TypeError(f"{info.field_name} should be a string")

        if not v.strip():
            raise ValueError(f"{info.field_name} should not be empty")

        return v


class GetSessionReq(BaseModel):
    user_id: UUID
    token: str

    @field_validator("token", mode="before")
    def check_token(cls, v, info):
        if not v or not isinstance(v, str):
            raise TypeError(f"{info.field_name} should be string")

        if not v.strip():
            raise ValueError(f"{info.field_name} can not be empty")

        return v.strip()

    @field_validator("user_id", mode="before")
    def check_user_id(cls, v, info):
        if v is None:
            raise ValueError(f"{info.field_name} cannot be empty")
        try:
            return UUID(str(v))
        except ValueError:
            raise ValueError(f"{info.field_name} must be a valid UUID")
