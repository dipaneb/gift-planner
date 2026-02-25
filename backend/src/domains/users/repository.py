from typing import Annotated
import uuid
from datetime import datetime
from decimal import Decimal

from fastapi import Depends
from sqlalchemy import select, update, func
from sqlalchemy.orm import Session

from src.infrastructure.database.session import get_db
from src.domains.auth.password_handler import get_password_hash
from src.domains.gifts.models import Gift
from src.domains.gifts.enums import GiftStatusEnum
from .models import User

class UserRepository:
    def __init__(self, db: Annotated[Session, Depends(get_db)]):
        self.db = db
            
    def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        return self.db.execute(stmt).scalar_one_or_none()
    
    def get_by_id(self, user_id: uuid.UUID) -> User | None:
        stmt = select(User).where(User.id == user_id)
        return self.db.execute(stmt).scalar_one_or_none()
    
    def get_by_verification_token(self, raw_token: str) -> User | None:
        """Get user by verifying the raw token against stored Argon2 hashes."""
        from src.domains.auth.verification_token_handler import verify_verification_token
        
        stmt = select(User).where(
            User.verification_token_hash.is_not(None),
            User.is_verified == False
        )
        users = self.db.execute(stmt).scalars().all()
        
        for user in users:
            if user.verification_token_hash and verify_verification_token(raw_token, user.verification_token_hash):
                return user
        return None
    
    def create(self, user: User) -> User:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def set_password(self, user_id: uuid.UUID, new_plain_password: str) -> None:
        new_hashed_password = get_password_hash(new_plain_password)
        stmt = update(User).where(User.id == user_id).values(password_hash=new_hashed_password)
        self.db.execute(stmt)
        self.db.commit()

    def set_budget(self, user_id: uuid.UUID, budget: Decimal | None) -> User:
        stmt = update(User).where(User.id == user_id).values(budget=budget)
        self.db.execute(stmt)
        self.db.commit()
        return self.get_by_id(user_id)

    def get_spent_amount(self, user_id: uuid.UUID) -> Decimal:
        """Calculate total spent from gifts that are no longer just ideas."""
        stmt = (
            select(func.coalesce(func.sum(Gift.price * Gift.quantity), 0))
            .where(Gift.user_id == user_id)
            .where(Gift.status != GiftStatusEnum.idee)
            .where(Gift.price.is_not(None))
        )
        result = self.db.execute(stmt).scalar_one()
        return Decimal(str(result))

    def update_name(self, user_id: uuid.UUID, name: str) -> User:
        """Update the user's display name."""
        stmt = update(User).where(User.id == user_id).values(name=name)
        self.db.execute(stmt)
        self.db.commit()
        return self.get_by_id(user_id)

    def delete_name(self, user_id: uuid.UUID) -> User:
        """Remove the user's display name (set to null)."""
        stmt = update(User).where(User.id == user_id).values(name=None)
        self.db.execute(stmt)
        self.db.commit()
        return self.get_by_id(user_id)

    def set_verification_token(self, user_id: uuid.UUID, token_hash: str, expires_at: datetime) -> None:
        """Set email verification token for a user."""
        stmt = update(User).where(User.id == user_id).values(
            verification_token_hash=token_hash,
            verification_token_expires_at=expires_at
        )
        self.db.execute(stmt)
        self.db.commit()

    def verify_email(self, user_id: uuid.UUID) -> None:
        """Mark user's email as verified."""
        stmt = update(User).where(User.id == user_id).values(
            is_verified=True,
            verification_token_hash=None,
            verification_token_expires_at=None
        )
        self.db.execute(stmt)
        self.db.commit()

