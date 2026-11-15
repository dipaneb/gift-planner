from __future__ import annotations

from typing import TYPE_CHECKING
import uuid

from sqlalchemy import (
    String,
    Text,
    ForeignKey,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.database.base import Base

if TYPE_CHECKING:
    # Only for type checkers: importing them at runtime would be circular.
    from src.domains.gifts.models import Gift
    from src.domains.groups.models import Group
    from src.domains.users.models import User


class Recipient(Base):
    __tablename__ = "recipients"

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

    notes: Mapped[str | None] = mapped_column(
        Text,
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="recipients"
    )

    groups: Mapped[list["Group"]] = relationship(
        "Group",
        secondary="group_members",
        back_populates="members",
    )

    gifts: Mapped[list["Gift"]] = relationship(
        "Gift",
        secondary="gift_recipients",
        back_populates="recipients",
    )

    __table_args__ = (
        Index("idx_recipients_user", "user_id"),
        Index("idx_recipients_name", "name"),
    )

class GroupMember(Base):
    __tablename__ = "group_members"

    group_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("groups.id", ondelete="CASCADE"),
        primary_key=True,
    )

    recipient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("recipients.id", ondelete="CASCADE"),
        primary_key=True,
    )

    __table_args__ = (
        Index("idx_group_members_recipient", "recipient_id"),
    )

class GiftRecipient(Base):
    __tablename__ = "gift_recipients"

    gift_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("gifts.id", ondelete="CASCADE"),
        primary_key=True,
    )

    recipient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("recipients.id", ondelete="CASCADE"),
        primary_key=True,
    )

    __table_args__ = (
        Index("idx_gift_recipients_recipient", "recipient_id"),
    )
