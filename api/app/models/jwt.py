"""JWT-related Pydantic models.

Contains token payload models for access and refresh tokens.
"""

from pydantic import EmailStr, field_validator
from app.core.pydantic import CustomBaseModel


class Tokens(CustomBaseModel):
    """JWT token payload model.

    Attributes:
        user_id: UUID string of the user.
        email: User's email address.
    """

    user_id: str
    email: EmailStr

    @field_validator("email", "user_id", mode="before")
    def verify_fields(cls, v, info):
        """Validate email and user_id are non-empty strings."""
        if not isinstance(v, str):
            raise TypeError(f"{info.field_name} must be a string")

        if not v.strip():
            raise ValueError(f"{info.field_name} cannot be empty or whitespace")

        return v.strip()
