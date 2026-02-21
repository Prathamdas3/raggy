from pydantic import EmailStr, field_validator
from app.core.pydantic import CustomBaseModel


class Tokens(CustomBaseModel):
    user_id: str
    email: EmailStr

    @field_validator("email", "user_id", mode="before")
    def verify_fields(cls, v, info):
        if not isinstance(v, str):
            raise TypeError(f"{info.field_name} must be a string")

        if not v.strip():
            raise ValueError(f"{info.field_name} cannot be empty or whitespace")

        return v.strip()
