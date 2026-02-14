from typing import Annotated
import uuid
from decimal import Decimal

from fastapi import Depends, HTTPException, status

from .repository import UserRepository
from .schemas import UserRead


class UserService:
    def __init__(self, user_repo: Annotated[UserRepository, Depends()]):
        self.user_repo = user_repo

    def _build_user_read(self, user_id: uuid.UUID) -> UserRead | None:
        """Build UserRead with computed spent and remaining."""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return None
        
        spent = self.user_repo.get_spent_amount(user_id)
        remaining = user.budget - spent if user.budget is not None else None
        
        return UserRead(
            id=user.id,
            email=user.email,
            name=user.name,
            budget=user.budget,
            spent=spent,
            remaining=remaining,
        )

    def update_budget(self, user_id: uuid.UUID, budget: Decimal) -> UserRead:
        self.user_repo.set_budget(user_id, budget)
        return self._build_user_read(user_id)

    def delete_budget(self, user_id: uuid.UUID) -> UserRead:
        self.user_repo.set_budget(user_id, None)
        return self._build_user_read(user_id)

    def get_current_user(self, user_id: uuid.UUID) -> UserRead:
        """Get current user with computed budget fields."""
        return self._build_user_read(user_id)

    def update_name(self, user_id: uuid.UUID, name: str) -> UserRead:
        """Update user's display name."""
        self.user_repo.update_name(user_id, name)
        return self._build_user_read(user_id)

    def update_password(self, user_id: uuid.UUID, current_password: str, new_password: str) -> None:
        """Update user's password after verifying current password."""
        from src.domains.auth.password_handler import verify_password
        
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        if not verify_password(current_password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect")
        
        self.user_repo.set_password(user_id, new_password)
