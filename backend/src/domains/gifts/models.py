from __future__ import annotations
import uuid
from decimal import Decimal

from sqlalchemy import (
    String,
    Integer,
    Numeric,
    ForeignKey,
    CheckConstraint,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.database.base import Base
from src.domains.gifts.enums import GiftStatusEnum, GiftStatus

class Gift(Base):
    __tablename__ = "gifts"

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

    url: Mapped[str | None] = mapped_column(
        String(255),
    )

    price: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2)
    )

    status: Mapped[GiftStatusEnum] = mapped_column(
        GiftStatus,
        nullable=False,
        default="idee",
    )

    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="gifts"
    )

    recipients: Mapped[list["Recipient"]] = relationship(
        "Recipient",
        secondary="gift_recipients",
        back_populates="gifts",
    )

    __table_args__ = (
        CheckConstraint("quantity >= 1", name="ck_gifts_quantity"),
        CheckConstraint("price >= 0", name="ck_gifts_price"),
        Index("idx_gifts_user", "user_id"),
        Index("idx_gifts_status", "status"),
    )
