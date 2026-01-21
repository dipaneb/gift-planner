# from __future__ import annotations

from typing import Annotated
from fastapi import APIRouter, Depends

from src.domains.auth.dependencies import get_current_user
from .models import User
from .schemas import UserRead

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserRead)
def me(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    return current_user
