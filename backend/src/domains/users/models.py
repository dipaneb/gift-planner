from __future__ import annotations
import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, DateTime, Numeric, String, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.database.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    name: Mapped[str | None] = mapped_column(
        String(255),
    )

    budget: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2),
    )

    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    verification_token_fingerprint: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
        unique=True,
        index=True,
    )

    verification_token_hash: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    verification_token_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    groups: Mapped[list["Group"]] = relationship(
        "Group",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    recipients: Mapped[list["Recipient"]] = relationship(
        "Recipient",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    gifts: Mapped[list["Gift"]] = relationship(
        "Gift",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(
        "RefreshToken",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        CheckConstraint("budget > 0", name="ck_users_budget_positive"),
    )
