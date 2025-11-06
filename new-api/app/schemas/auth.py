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
    def check_uuid(cls, v):
        if not isinstance(v, UUID):
            raise TypeError("user_id must be a UUID")
        return v

    @field_validator("expires_at")
    def check_datetime(cls, v):
        if not isinstance(v, datetime):
            raise TypeError("expires_at must be a datetime")
        return v


class SignIn(BaseModel):
    email: EmailStr
    password: str

    @field_validator("email", mode="before")
    def verify_email(cls, v, field):
        if not isinstance(v, EmailStr):
            raise TypeError(f"{field.name} must follow the email format")

        if not v.strip():
            raise ValueError(f"{field.name} should not be empty")

        return v.strip()

    @field_validator("password", mode="before")
    def verify_password(cls, v, field):
        if not v or not isinstance(v, str):
            raise TypeError(f"{field.name} should be a string")

        if not v.strip():
            raise ValueError(f"{field.name} should not be empty")


class GetSessionReq(BaseModel):
    user_id: UUID
    token: str

    @field_validator("token", mode="before")
    def check_token(cls, v, field):
        if not v or not isinstance(v, str):
            raise TypeError(f"{field.name} should be string")

        if not v.strip():
            raise ValueError(f"{field.name} can not be empty")

        return v.strip()

    @field_validator("user_id", mode="before")
    def check_user_id(cls, v, field):
        if not v or not isinstance(v, UUID):
            raise TypeError(f"{field.name} should be UUID")

        return v
