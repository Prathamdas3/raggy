from sqlmodel import Field, SQLModel, Relationship
from pydantic import EmailStr
from enum import Enum
import sqlalchemy as sa
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional
from sqlalchemy.orm import declared_attr


class Sender(Enum):
    user = "user"
    llm = "llm"
    system = "system"


class Status(Enum):
    init = "init"
    error = "error"
    success = "success"
    pending = "pending"




class CreatedAtMixin:
    __allow_unmapped__ = True

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    @declared_attr
    def created_at(cls):
        return sa.Column(
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        )


class UpdatedAtMixin:
    __allow_unmapped__ = True

    @declared_attr
    def updated_at(cls):
        return sa.Column(
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        )


class Users(CreatedAtMixin, SQLModel, table=True):
    email: EmailStr = Field(
        default="",
        sa_column=sa.Column(sa.String(), nullable=False, index=True, unique=True),
    )
    password: str = Field(nullable=False)
    username: str = Field(nullable=False)

    # Relationships
    sessions: list["Sessions"] = Relationship(back_populates="user")
    docs: list["Docs"] = Relationship(back_populates="user")
    chats: list["Chats"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"foreign_keys": "[Chats.created_by]"},
    )
    summaries: list["DocumentSummaries"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"foreign_keys": "[DocumentSummaries.created_by]"},
    )
    chat_branches: list["ChatBranches"] = Relationship(back_populates="user")
    messages: list["Messages"] = Relationship(back_populates="sender")
    message_revisions: list["MessageRevisions"] = Relationship(back_populates="editor")


class Sessions(CreatedAtMixin, SQLModel, table=True):
    expires_at: datetime | None = Field(default=None, nullable=False)
    token: str = Field(default="")

    # Foreign keys
    user_id: UUID = Field(foreign_key="users.id", nullable=False)

    # Relationships
    user: Users = Relationship(back_populates="sessions")


class Docs(CreatedAtMixin, SQLModel, table=True):
    original_text: str = Field(default="")
    proccessing_status: Status = Field(
        sa_column=sa.Column(sa.Enum(Status), nullable=False)
    )

    # Foreign keys
    user_id: UUID = Field(foreign_key="users.id", nullable=False)

    # Relationships
    user: Users = Relationship(back_populates="docs")
    chat: Optional["Chats"] = Relationship(back_populates="docs")
    summaries: list["DocumentSummaries"] = Relationship(back_populates="docs")



class Chats(CreatedAtMixin, UpdatedAtMixin, SQLModel, table=True):
    title: str = Field(default="")
    is_bookmarked: bool = Field(default=False)
    share_id: str | None = Field(default=None)

    # Foreign keys
    docs_id: UUID = Field(foreign_key="docs.id", unique=True, nullable=False)
    created_by: UUID = Field(foreign_key="users.id", nullable=False)
    # Nullable on creation — set after the first branch is created
    active_branch_id: UUID | None = Field(
        default=None,
        foreign_key="chatbranches.id",
        nullable=True,
    )

    # Relationships
    docs: Docs = Relationship(back_populates="chat")
    user: Users = Relationship(
        back_populates="chats",
        sa_relationship_kwargs={"foreign_keys": "[Chats.created_by]"},
    )
    branches: list["ChatBranches"] = Relationship(
        back_populates="chat",
        sa_relationship_kwargs={"foreign_keys": "[ChatBranches.chat_id]"},
    )


class DocumentSummaries(CreatedAtMixin, SQLModel, table=True):
    # Foreign keys
    docs_id: UUID = Field(foreign_key="docs.id", nullable=False)
    created_by: UUID = Field(foreign_key="users.id", nullable=False)

    # Relationships
    docs: Docs = Relationship(back_populates="summaries")
    user: Users = Relationship(
        back_populates="summaries",
        sa_relationship_kwargs={"foreign_keys": "[DocumentSummaries.created_by]"},
    )
    summaryvarient: list["SummaryVarients"] = Relationship(back_populates="summary")



class SummaryVarients(CreatedAtMixin, SQLModel, table=True):
    content: str = Field(default="")
    audio_url: str = Field(default="")

    # Foreign keys
    summary_id: UUID = Field(foreign_key="documentsummaries.id", nullable=False)

    # Relationships
    summary: DocumentSummaries = Relationship(back_populates="summaryvarient")



class ChatBranches(CreatedAtMixin, SQLModel, table=True):
    chat_id: UUID = Field(foreign_key="chats.id", nullable=False)
    parent_branch_id: UUID | None = Field(
        default=None,
        foreign_key="chatbranches.id",
        nullable=True,
    )
    forked_from_message_id: UUID | None = Field(
        default=None,
        foreign_key="messages.id",
        nullable=True,
    )
    created_by: UUID = Field(foreign_key="users.id", nullable=False)

    # Relationships
    chat: Chats = Relationship(
        back_populates="branches",
        sa_relationship_kwargs={"foreign_keys": "[ChatBranches.chat_id]"},
    )
    user: Users = Relationship(back_populates="chat_branches")
    child_branches: list["ChatBranches"] = Relationship(
        back_populates="parent_branch",
        sa_relationship_kwargs={"foreign_keys": "[ChatBranches.parent_branch_id]"},
    )
    parent_branch: Optional["ChatBranches"] = Relationship(
        back_populates="child_branches",
        sa_relationship_kwargs={"foreign_keys": "[ChatBranches.parent_branch_id]"},
    )
    messages: list["Messages"] = Relationship(back_populates="branch")



class Messages(CreatedAtMixin, SQLModel, table=True):
    role: Sender = Field(
        sa_column=sa.Column(sa.Enum(Sender), nullable=False)
    )
    deleted_at: datetime | None = Field(
        default=None,
        sa_column=sa.Column(sa.DateTime(timezone=True), nullable=True),
    )
    latest_revision_id: UUID | None = Field(default=None, nullable=True)

    # Foreign keys
    branch_id: UUID = Field(foreign_key="chatbranches.id", nullable=False)
    sender_id: UUID | None = Field(  
        default=None,
        foreign_key="users.id",
        nullable=True,
    )
    reply_to_message_id: UUID | None = Field(  
        default=None,
        foreign_key="messages.id",
        nullable=True,
    )

    # Relationships
    branch: ChatBranches = Relationship(back_populates="messages")
    sender: Optional[Users] = Relationship(back_populates="messages")
    revisions: list["MessageRevisions"] = Relationship(back_populates="message")
    replies: list["Messages"] = Relationship(
        back_populates="reply_to",
        sa_relationship_kwargs={"foreign_keys": "[Messages.reply_to_message_id]"},
    )
    reply_to: Optional["Messages"] = Relationship(
        back_populates="replies",
        sa_relationship_kwargs={"foreign_keys": "[Messages.reply_to_message_id]"},
    )


class MessageRevisions(CreatedAtMixin, SQLModel, table=True):
    content: str = Field(default="")
    audio_url: str = Field(default="")

    # Foreign keys
    message_id: UUID = Field(foreign_key="messages.id", nullable=False)
    edited_by: UUID | None = Field( 
        default=None,
        foreign_key="users.id",
        nullable=True,
    )

    # Relationships
    message: Messages = Relationship(back_populates="revisions")
    editor: Optional[Users] = Relationship(back_populates="message_revisions")
