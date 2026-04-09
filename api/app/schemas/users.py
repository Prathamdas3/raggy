from sqlmodel import Field, Relationship, SQLModel
from pydantic import EmailStr
import sqlalchemy as sa
from typing import TYPE_CHECKING
from .chats import Chats
from .common import CreatedAtMixin

if TYPE_CHECKING:
    from .sessions import Sessions


class Users(CreatedAtMixin, SQLModel, table=True):
    """User account model.

    Attributes:
        email: Unique email address.
        password: Hashed password.
        sessions: Related sessions.
        chats: Related chat conversations.
    """

    email: EmailStr = Field(
        sa_column=sa.Column(sa.String(), nullable=False, index=True, unique=True)
    )
    password: str = Field(nullable=False)

    sessions: list["Sessions"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

    chats: list["Chats"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
