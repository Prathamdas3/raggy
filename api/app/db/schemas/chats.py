from uuid import UUID
from sqlmodel import Field, Relationship, SQLModel
import sqlalchemy as sa
from typing import Optional,TYPE_CHECKING
from .common import CreatedAtMixin, UpdatedAtMixin, Status
from .summaries import SummaryVariants
from .messages import Messages


if TYPE_CHECKING: 
    from .users import Users

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

    is_bookmarked: bool = Field(default=False,index=True)
    share_id: str | None = Field(default=None,index=True)

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
            sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False,index=True
        )
    )

    user: "Users" = Relationship(back_populates="chats")

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
            sa.ForeignKey("chats.id", ondelete="CASCADE"), nullable=False,index=True
        )
    )

    parent_branch_id: UUID | None = Field(
        default=None,
        sa_column=sa.Column(
            sa.ForeignKey("chatbranches.id", ondelete="CASCADE"), nullable=True,index=True
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
