from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy import select, delete, func
from sqlalchemy.orm import Session

from src.infrastructure.database.session import get_db
from .models import Gift


class GiftRepository:
    def __init__(self, db: Annotated[Session, Depends(get_db)]):
        self.db = db

    def create(self, new_gift: Gift) -> Gift:
        self.db.add(new_gift)
        self.db.commit()
        self.db.refresh(new_gift)
        return new_gift

    def get(self, pagination: dict, gift_user_id: UUID) -> tuple[list[Gift], int]:
        sort = pagination["sort"]
        page = pagination["page"]
        limit = pagination["limit"]

        # Base query with filter
        base_stmt = select(Gift).where(Gift.user_id == gift_user_id)

        # Count query - optimized to only count IDs
        count_stmt = select(func.count(Gift.id)).where(Gift.user_id == gift_user_id)
        total = self.db.execute(count_stmt).scalar() or 0

        # Items query with sorting and pagination
        stmt = base_stmt
        if sort == "asc":
            stmt = stmt.order_by(Gift.name.asc())
        elif sort == "desc":
            stmt = stmt.order_by(Gift.name.desc())
        else:
            stmt = stmt.order_by(Gift.created_at.desc())

        stmt = stmt.offset((page - 1) * limit).limit(limit)

        gifts = self.db.execute(stmt).scalars().all()
        return list(gifts), total

    def get_by_id(self, gift_user_id: UUID, gift_id: UUID) -> Gift | None:
        stmt = select(Gift).where(
            Gift.user_id == gift_user_id,
            Gift.id == gift_id
        )
        gift = self.db.execute(stmt).scalar_one_or_none()
        return gift

    def update(self, gift: Gift) -> Gift:
        """Update existing gift in database."""
        self.db.commit()
        self.db.refresh(gift)
        return gift

    def delete(self, gift_user_id: UUID, gift_id: UUID) -> bool:
        """
        Delete a gift by ID.
        Returns True if deleted, False if not found.
        """
        stmt = delete(Gift).where(
            Gift.user_id == gift_user_id,
            Gift.id == gift_id
        )
        result = self.db.execute(stmt)
        self.db.commit()
        return result.rowcount > 0
