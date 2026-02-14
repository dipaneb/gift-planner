from typing import Annotated
import uuid
from decimal import Decimal

from fastapi import Depends

from .repository import UserRepository
from .schemas import UserRead


class UserService:
    def __init__(self, user_repo: Annotated[UserRepository, Depends()]):
        self.user_repo = user_repo

    def update_budget(self, user_id: uuid.UUID, budget: Decimal) -> UserRead:
        user = self.user_repo.set_budget(user_id, budget)
        return UserRead.model_validate(user)

    def delete_budget(self, user_id: uuid.UUID) -> UserRead:
        user = self.user_repo.set_budget(user_id, None)
        return UserRead.model_validate(user)
