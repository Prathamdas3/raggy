"""Database schema definitions using SQLModel.

Contains all ORM models for the application including Users, Sessions,
Chats, Messages, and their relationships.
"""

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
    """Message sender type enumeration.

    Attributes:
        user: Message sent by a user.
        llm: Message sent by the LLM.
        system: System-generated message.
    """

    user = "user"
    llm = "llm"
    system = "system"


class Status(Enum):
    """Processing status enumeration.

    Attributes:
        init: Initial state.
        error: Error state.
        success: Success state.
        pending: Pending processing.
    """

    init = "init"
    error = "error"
    success = "success"
    pending = "pending"


class VariantType(Enum):
    """Summary variant type enumeration.

    Attributes:
        short: Short summary.
        long: Long summary.
        detailed: Detailed summary.
    """

    short = "short"
    long = "long"
    detailed = "detailed"
    default="default"


# ---------------- MIXINS ----------------


class CreatedAtMixin:
    """Mixin for adding id and created_at timestamp to models.

    Adds:
        - id: UUID primary key with auto-generation
        - created_at: DateTime with server-default timestamp
    """

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
    """Mixin for adding updated_at timestamp to models.

    Adds:
        - updated_at: DateTime with server-default and auto-update
    """

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


# ---------------- SESSIONS ----------------


class Sessions(CreatedAtMixin, SQLModel, table=True):
    """User session model for token management.

    Attributes:
        expires_at: Session expiration timestamp.
        token: Session token string.
        user_id: Foreign key to users table.
        user: Related user.
    """

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
    """Chat conversation model (root entity).

    Attributes:
        title: Chat title.
        original_doc: Original doc content.
        is_bookmarked: Bookmark flag.
        share_id: Optional share identifier.
        processing_status: Processing status.
        active_branch_id: Current conversation branch.
        user_id: Foreign key to users table.
        user: Related user.
        branches: Related chat branches.
        summaries: Related summary variants.
    """

    title: str = Field(default="")
    original_doc: str = Field(default="")
    shared_doc:str=Field(default="")

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
        back_populates="chat",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan",
            "foreign_keys": "[ChatBranches.chat_id]",
        },
    )

    summaries: list["SummaryVariants"] = Relationship(
        back_populates="chat", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )


# ---------------- SUMMARY VARIANTS ----------------


class SummaryVariants(CreatedAtMixin, SQLModel, table=True):
    """Chat summary variant model.

    Attributes:
        content: Summary text content.
        audio_url: Optional audio URL for the summary.
        variant_type: Type of summary (short, long, detailed).
        chat_id: Foreign key to chats table.
        chat: Related chat.
    """

    content: str = Field(default="")
    audio_url: str = Field(default="")

    variant_type: VariantType = Field(
        default=VariantType.default,
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
    """Chat branch model for conversation branching.

    Attributes:
        chat_id: Foreign key to chats table.
        parent_branch_id: Optional parent branch for tree structure.
        chat: Related chat.
        child_branches: Child branches in the tree.
        parent_branch: Parent branch in the tree.
        messages: Related messages.
    """

    chat_id: UUID = Field(
        sa_column=sa.Column(
            sa.ForeignKey("chats.id", ondelete="CASCADE"), nullable=False
        )
    )

    parent_branch_id: UUID | None = Field(
        default=None,
        sa_column=sa.Column(
            sa.ForeignKey("chatbranches.id", ondelete="CASCADE"), nullable=True
        ),
    )

    chat: Chats = Relationship(
        back_populates="branches",
        sa_relationship_kwargs={
            "foreign_keys": "[ChatBranches.chat_id]",
        },
    )

    child_branches: list["ChatBranches"] = Relationship(
        back_populates="parent_branch",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )

    parent_branch: Optional["ChatBranches"] = Relationship(
        back_populates="child_branches",
        sa_relationship_kwargs={"remote_side": "ChatBranches.id"},
    )

    messages: list["Messages"] = Relationship(
        back_populates="branch",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


# ---------------- MESSAGES ----------------


class Messages(CreatedAtMixin, SQLModel, table=True):
    """Chat message model.

    Attributes:
        role: Message sender type (user, llm, system).
        branch_id: Foreign key to chatbranches table.
        sender_id: Optional user who sent the message.
        reply_to_message_id: Optional parent message for replies.
        branch: Related chat branch.
        revisions: Message revision history.
        replies: Direct replies to this message.
        reply_to: Parent message this is replying to.
    """

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

    reply_to: Optional["Messages"] = Relationship(
        back_populates="replies",
        sa_relationship_kwargs={"remote_side": "Messages.id"},
    )


# ---------------- MESSAGE REVISIONS ----------------


class MessageRevisions(CreatedAtMixin, SQLModel, table=True):
    """Message revision model for edit history.

    Attributes:
        content: Revised message content.
        audio_url: Optional audio URL.
        message_id: Foreign key to messages table.
        edited_by: User who made the revision.
        message: Related message.
    """

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
