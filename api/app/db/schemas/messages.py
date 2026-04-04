import sqlalchemy as sa
from sqlmodel import Field, Relationship, SQLModel
from uuid import UUID
from typing import Optional,TYPE_CHECKING
from .common import CreatedAtMixin, Sender

if TYPE_CHECKING:
    from .chats import ChatBranches

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
            sa.ForeignKey("chatbranches.id", ondelete="CASCADE"), nullable=False,index=True
        )
    )

    sender_id: UUID | None = Field(
        sa_column=sa.Column(
            sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True,index=True
        )
    )

    reply_to_message_id: UUID | None = Field(
        sa_column=sa.Column(
            sa.ForeignKey("messages.id", ondelete="CASCADE"), nullable=True,index=True
        )
    )

    branch: "ChatBranches" = Relationship(back_populates="messages")

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
            sa.ForeignKey("messages.id", ondelete="CASCADE"), nullable=False,index=True
        )
    )

    edited_by: UUID | None = Field(
        sa_column=sa.Column(
            sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True,index=True
        )
    )

    message: Messages = Relationship(back_populates="revisions")
