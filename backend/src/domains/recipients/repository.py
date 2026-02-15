from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy import select, delete, func
from sqlalchemy.orm import Session

from src.infrastructure.database.session import get_db
from .models import Recipient


class RecipientRepository:
    def __init__(self, db: Annotated[Session, Depends(get_db)]):
        self.db = db

    def create(self, new_recipient: Recipient) -> Recipient:
        self.db.add(new_recipient)
        self.db.commit()
        self.db.refresh(new_recipient)
        return new_recipient

    def get(self, pagination: dict, recipient_user_id: UUID) -> tuple[list[Recipient], int]:
        sort = pagination["sort"]
        page = pagination["page"]
        limit = pagination["limit"]
        
        # Base query with filter
        base_stmt = select(Recipient).where(Recipient.user_id == recipient_user_id)
        
        # Count query - optimized to only count IDs
        count_stmt = select(func.count(Recipient.id)).where(Recipient.user_id == recipient_user_id)
        total = self.db.execute(count_stmt).scalar() or 0
        
        # Items query with sorting and pagination
        stmt = base_stmt
        if sort == "asc":
            stmt = stmt.order_by(Recipient.name.asc())
        elif sort == "desc":
            stmt = stmt.order_by(Recipient.name.desc())
        else:
            stmt = stmt.order_by(Recipient.created_at.desc())
        
        stmt = stmt.offset((page - 1) * limit).limit(limit)
        
        recipients = self.db.execute(stmt).scalars().all()
        return list(recipients), total
    
    def get_by_id(self, recipient_user_id: UUID, recipient_id: UUID) -> Recipient | None:
        stmt = select(Recipient).where(
            Recipient.user_id == recipient_user_id,
            Recipient.id == recipient_id
        )
        recipient = self.db.execute(stmt).scalar_one_or_none()
        return recipient
    
    def update(self, recipient: Recipient) -> Recipient:
        """Update existing recipient in database."""
        self.db.commit()
        self.db.refresh(recipient)
        return recipient
    
    def delete(self, recipient_user_id: UUID, recipient_id: UUID) -> bool:
        """
        Delete a recipient by ID.
        Returns True if deleted, False if not found.
        """
        stmt = delete(Recipient).where(
            Recipient.user_id == recipient_user_id,
            Recipient.id == recipient_id
        )
        result = self.db.execute(stmt)
        self.db.commit()
        return result.rowcount > 0
