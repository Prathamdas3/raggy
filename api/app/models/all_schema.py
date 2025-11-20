from typing import Optional
from sqlmodel import Field, SQLModel, Column, Relationship
from uuid import UUID, uuid4
from datetime import datetime
from enum import Enum
import sqlalchemy as sa
from pydantic import EmailStr


class Type(Enum):
    reset = "reset-password"
    verification = "email-verification"


class Sender(Enum):
    user = "user"
    llm = "llm"


class User(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    first_name: str | None = Field(default=None, nullable=True)
    last_name: str | None = Field(default=None, nullable=True)
    user_name: str = Field(default="", index=True)
    password: str = ""
    email: EmailStr = Field(
        default="", sa_type=sa.String(), nullable=False, index=True, unique=True
    )

    # Relationships
    sessions: list["Session"] = Relationship(back_populates="user", cascade_delete=True)
    chats: list["Chats"] = Relationship(back_populates="user", cascade_delete=True)
    docs: list["Docs"] = Relationship(back_populates="user", cascade_delete=True)
    messages: list["Messages"] = Relationship(
        back_populates="user", cascade_delete=True
    )

    created_at: datetime | None = Field(
        default=None,
        sa_type=sa.DateTime(timezone=True),
        sa_column_kwargs={"server_default": sa.func.now()},
        nullable=False,
    )
    updated_at: datetime | None = Field(
        default=None,
        sa_type=sa.DateTime(timezone=True),
        sa_column_kwargs={"onupdate": sa.func.now(), "server_default": sa.func.now()},
    )


class Session(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", nullable=False)
    expires_at: datetime | None = Field(default=None, nullable=False)
    token: str = ""
    ip_address: str = ""
    user_agent: str = ""

    # Relationship
    user: User = Relationship(back_populates="sessions")

    created_at: datetime | None = Field(
        default=None,
        sa_type=sa.DateTime(timezone=True),
        sa_column_kwargs={"server_default": sa.func.now()},
        nullable=False,
    )
    updated_at: datetime | None = Field(
        default=None,
        sa_type=sa.DateTime(timezone=True),
        sa_column_kwargs={"onupdate": sa.func.now(), "server_default": sa.func.now()},
    )


class Token(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", nullable=False)
    type: Type = Field(sa_column=Column(sa.Enum(Type), nullable=False))
    token: str = Field(default="")
    created_at: datetime | None = Field(
        default=None,
        sa_type=sa.DateTime(timezone=True),
        sa_column_kwargs={"server_default": sa.func.now()},
        nullable=False,
    )
    updated_at: datetime | None = Field(
        default=None,
        sa_type=sa.DateTime(timezone=True),
        sa_column_kwargs={"onupdate": sa.func.now(), "server_default": sa.func.now()},
    )


class Chats(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", nullable=False)
    chat_name: str | None = None
    is_bookmarked: bool = False
    share_id: str | None = Field(default=None, unique=True, nullable=True)

    # Relationships
    user: User = Relationship(back_populates="chats")
    # FIXED: Changed from "chats" to "chat" to match the property name in Docs model
    doc: Optional["Docs"] = Relationship(back_populates="chat", cascade_delete=True)
    messages: list["Messages"] = Relationship(
        back_populates="chat", cascade_delete=True
    )

    created_at: datetime | None = Field(
        default=None,
        sa_type=sa.DateTime(timezone=True),
        sa_column_kwargs={"server_default": sa.func.now()},
        nullable=False,
    )
    updated_at: datetime | None = Field(
        default=None,
        sa_type=sa.DateTime(timezone=True),
        sa_column_kwargs={"onupdate": sa.func.now(), "server_default": sa.func.now()},
    )


class Docs(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", nullable=False)
    chat_id: UUID = Field(
        foreign_key="chats.id",
        nullable=False,
        unique=True,
    )
    original_text: str = Field(default="", sa_type=sa.Text())
    summary_text: str = Field(default="", sa_type=sa.Text())
    audio_url: str = Field(default="", sa_type=sa.String())

    # Relationships
    user: User = Relationship(back_populates="docs")
    chat: Chats = Relationship(back_populates="doc")

    created_at: datetime | None = Field(
        default=None,
        sa_type=sa.DateTime(timezone=True),
        sa_column_kwargs={"server_default": sa.func.now()},
        nullable=False,
    )
    updated_at: datetime | None = Field(
        default=None,
        sa_type=sa.DateTime(timezone=True),
        sa_column_kwargs={"onupdate": sa.func.now(), "server_default": sa.func.now()},
    )


class Messages(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    chat_id: UUID = Field(foreign_key="chats.id", nullable=False)
    user_id: UUID = Field(foreign_key="user.id", nullable=False)
    question_id: Optional[UUID] = Field(
        foreign_key="messages.id", default=None, nullable=True
    )
    sender: Sender = Field(sa_column=Column(sa.Enum(Sender), nullable=False))
    content: str = ""
    audio_url: str = ""

    # Relationships
    # FIXED: Changed from "chats" to "chat" to match the property name
    chat: Chats = Relationship(back_populates="messages")
    user: User = Relationship(back_populates="messages")

    created_at: datetime | None = Field(
        default=None,
        sa_type=sa.DateTime(timezone=True),
        sa_column_kwargs={"server_default": sa.func.now()},
        nullable=False,
    )
    updated_at: datetime | None = Field(
        default=None,
        sa_type=sa.DateTime(timezone=True),
        sa_column_kwargs={"onupdate": sa.func.now(), "server_default": sa.func.now()},
    )
