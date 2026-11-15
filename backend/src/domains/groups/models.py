from __future__ import annotations

from typing import TYPE_CHECKING
import uuid

from sqlalchemy import (
    String,
    ForeignKey,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.database.base import Base

if TYPE_CHECKING:
    # Only for type checkers: importing them at runtime would be circular.
    from src.domains.recipients.models import Recipient
    from src.domains.users.models import User


class Group(Base):
    __tablename__ = "groups"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="groups"
    )

    members: Mapped[list["Recipient"]] = relationship(
        "Recipient",
        secondary="group_members",
        back_populates="groups",
    )

    __table_args__ = (
        Index("idx_groups_user", "user_id"),
    )
