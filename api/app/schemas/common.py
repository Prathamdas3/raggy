from uuid import UUID,uuid4
from enum import Enum
from sqlalchemy.orm import declared_attr
from sqlmodel import Field
import sqlalchemy as sa 

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
        default: Default summary
    """

    short = "short"
    long = "long"
    detailed = "detailed"


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
            index=True,
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
