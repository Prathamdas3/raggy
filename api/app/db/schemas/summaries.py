import sqlalchemy as sa
from sqlmodel import Field, Relationship, SQLModel
from uuid import UUID
from typing import TYPE_CHECKING
from .common import CreatedAtMixin, VariantType

if TYPE_CHECKING:
    from .chats import Chats



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
        default=VariantType.detailed,
        sa_column=sa.Column(sa.Enum(VariantType), nullable=False,index=True),
    )

    chat_id: UUID = Field(
        sa_column=sa.Column(
            sa.ForeignKey("chats.id", ondelete="CASCADE"), nullable=False,index=True
        )
    )

    chat: "Chats" = Relationship(back_populates="summaries")

    __table_args__ = (sa.UniqueConstraint("chat_id", "variant_type"),)
