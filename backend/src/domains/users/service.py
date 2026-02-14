from typing import Annotated
import uuid
from decimal import Decimal

from fastapi import Depends

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
