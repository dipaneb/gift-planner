from __future__ import annotations
import uuid

from sqlalchemy import String
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

    name: Mapped[str] = mapped_column(
        String(255),
    )

    # Relations (navigation uniquement)
    recipients: Mapped[list["recipient"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    groups: Mapped[list["Group"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    gifts: Mapped[list["Gift"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
