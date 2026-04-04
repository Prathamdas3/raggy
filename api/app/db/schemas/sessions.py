from sqlmodel import Field, Relationship, SQLModel
from uuid import UUID
from datetime import datetime
import sqlalchemy as sa
from .common import CreatedAtMixin
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .users import Users


class Sessions(CreatedAtMixin, SQLModel, table=True):
    """User session model for token management.

    Attributes:
        expires_at: Session expiration timestamp.
        token: Session token string.
        user_id: Foreign key to users table.
        user: Related user.
    """

    expires_at: datetime | None = Field(default=None, nullable=False, index=True)
    token: str = Field(default="",index=True)

    user_id: UUID = Field(
        sa_column=sa.Column(
            sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False,index=True
        )
    )

    user: "Users" = Relationship(back_populates="sessions")