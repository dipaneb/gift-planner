from typing import Annotated
import uuid
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

