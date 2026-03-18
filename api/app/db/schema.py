from celery.worker.strategy import default
from sqlmodel import Field, SQLModel, Relationship
from pydantic import EmailStr
from enum import Enum
import sqlalchemy as sa
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional
from sqlalchemy.orm import declared_attr


# ---------------- ENUMS ----------------


class Sender(Enum):
    user = "user"
    llm = "llm"
    system = "system"


class Status(Enum):
    init = "init"
    error = "error"
    success = "success"
    pending = "pending"


class VariantType(Enum):
    short = "short"
    long = "long"
    detailed = "detailed"


# ---------------- MIXINS ----------------


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


# ---------------- USERS ----------------


class Users(CreatedAtMixin, SQLModel, table=True):
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


# ---------------- SESSIONS ----------------


class Sessions(CreatedAtMixin, SQLModel, table=True):
    expires_at: datetime | None = Field(default=None, nullable=False)
    token: str = Field(default="")

    user_id: UUID = Field(
        sa_column=sa.Column(
            sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
        )
    )

    user: Users = Relationship(back_populates="sessions")


# ---------------- CHATS (ROOT ENTITY) ----------------


class Chats(CreatedAtMixin, UpdatedAtMixin, SQLModel, table=True):
    title: str = Field(default="")
    original_text: str = Field(default="")

    is_bookmarked: bool = Field(default=False)
    share_id: str | None = Field(default=None)

    processing_status: Status = Field(
        default=Status.init, sa_column=sa.Column(sa.Enum(Status), nullable=True)
    )

    # Active branch (current conversation path)
    active_branch_id: UUID | None = Field(
        default=None,
        foreign_key="chatbranches.id",
        nullable=True,
    )

    # Ownership
    user_id: UUID = Field(
        sa_column=sa.Column(
            sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
        )
    )

    user: Users = Relationship(back_populates="chats")

    # Relationships
    branches: list["ChatBranches"] = Relationship(
        back_populates="chat", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

    summaries: list["SummaryVariants"] = Relationship(
        back_populates="chat", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )


# ---------------- SUMMARY VARIANTS ----------------


class SummaryVariants(CreatedAtMixin, SQLModel, table=True):
    content: str = Field(default="")
    audio_url: str = Field(default="")

    variant_type: VariantType = Field(
        default=VariantType.short,
        sa_column=sa.Column(sa.Enum(VariantType), nullable=False),
    )

    chat_id: UUID = Field(
        sa_column=sa.Column(
            sa.ForeignKey("chats.id", ondelete="CASCADE"), nullable=False
        )
    )

    chat: Chats = Relationship(back_populates="summaries")

    __table_args__ = (sa.UniqueConstraint("chat_id", "variant_type"),)


# ---------------- CHAT BRANCHES ----------------


class ChatBranches(CreatedAtMixin, SQLModel, table=True):
    chat_id: UUID = Field(
        sa_column=sa.Column(
            sa.ForeignKey("chats.id", ondelete="CASCADE"), nullable=False
        )
    )

    parent_branch_id: UUID | None = Field(
        default=None,
        sa_column=sa.Column(
            sa.ForeignKey("chatbranches.id", ondelete="CASCADE"), nullable=True
        )
    )

    chat: Chats = Relationship(back_populates="branches")

    child_branches: list["ChatBranches"] = Relationship(
        back_populates="parent_branch",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )

    parent_branch: Optional["ChatBranches"] = Relationship(
        back_populates="child_branches"
    )

    messages: list["Messages"] = Relationship(
        back_populates="branch",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


# ---------------- MESSAGES ----------------


class Messages(CreatedAtMixin, SQLModel, table=True):
    role: Sender = Field(sa_column=sa.Column(sa.Enum(Sender), nullable=False))

    branch_id: UUID = Field(
        sa_column=sa.Column(
            sa.ForeignKey("chatbranches.id", ondelete="CASCADE"), nullable=False
        )
    )

    sender_id: UUID | None = Field(
        sa_column=sa.Column(
            sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True
        )
    )

    reply_to_message_id: UUID | None = Field(
        sa_column=sa.Column(
            sa.ForeignKey("messages.id", ondelete="CASCADE"), nullable=True
        )
    )

    branch: ChatBranches = Relationship(back_populates="messages")

    revisions: list["MessageRevisions"] = Relationship(
        back_populates="message",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )

    replies: list["Messages"] = Relationship(
        back_populates="reply_to",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )

    reply_to: Optional["Messages"] = Relationship(back_populates="replies")


# ---------------- MESSAGE REVISIONS ----------------


class MessageRevisions(CreatedAtMixin, SQLModel, table=True):
    content: str = Field(default="")
    audio_url: str = Field(default="")

    message_id: UUID = Field(
        sa_column=sa.Column(
            sa.ForeignKey("messages.id", ondelete="CASCADE"), nullable=False
        )
    )

    edited_by: UUID | None = Field(
        sa_column=sa.Column(
            sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True
        )
    )

    message: Messages = Relationship(back_populates="revisions")
