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
    first_name: str = ""
    last_name: str = ""
    user_name: str = Field(default="", nullable=False, index=True, unique=True)
    password: str = ""
    email: EmailStr = Field(
        default="", sa_type=sa.String(), nullable=False, index=True, unique=True
    )
    
    # Relationships
    session: "Session" = Relationship(back_populates="user", cascade_delete=True)
    chats: list["Chats"] = Relationship(back_populates="user", cascade_delete=True)
    docs: list["Docs"] = Relationship(back_populates="user", cascade_delete=True)
    messages: list["Messages"] = Relationship(back_populates="user", cascade_delete=True)
    
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
    user_id: UUID = Field(
        foreign_key="user.id", nullable=False
    )
    expires_at: datetime | None = Field(default=None, nullable=False)
    token: str = ""
    ip_address: str = ""
    user_agent: str = ""
    
    # Relationship
    user: User = Relationship(back_populates="session")
    
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
    user_id: UUID = Field(
        foreign_key="user.id", nullable=False
    )
    type: Type = Field(sa_column=Column(sa.Enum(Type),nullable=False))
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
    user_id: UUID = Field(
        foreign_key="user.id", nullable=False
    )
    chat_name: str = Field(default="", nullable=False)
    is_bookmarked: bool = False
    
    # Relationships
    user: User = Relationship(back_populates="chats")
    docs: "Docs" = Relationship(back_populates="chats", cascade_delete=True)
    messages: list["Messages"] = Relationship(back_populates="chats", cascade_delete=True)
    
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
    user_id: UUID = Field(
        foreign_key="user.id", nullable=False
    )
    chat_id: UUID = Field(
        foreign_key="chats.id", nullable=False, unique=True  # unique=True for 1:1
    )
    original_text: str = ""
    summary_text: str = ""
    audio_url: str = ""
    
    # Relationships
    user: User = Relationship(back_populates="docs")
    chat: Chats = Relationship(back_populates="docs")
    
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
    chat_id: UUID = Field(
        foreign_key="chats.id", nullable=False
    )
    user_id: UUID = Field(
        foreign_key="user.id", nullable=False
    )
    question_id: str = ""
    sender: Sender = Field(sa_column=Column(sa.Enum(Sender),nullable=False))
    content: str = ""
    audio_url: str = ""
    
    # Relationships
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