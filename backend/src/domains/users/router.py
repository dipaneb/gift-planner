# from __future__ import annotations

import uuid
from typing import Annotated
from fastapi import APIRouter, Depends, Response, status

from src.domains.auth.cookies import set_refresh_token_cookie
from src.domains.auth.dependencies import get_current_user_id
from src.domains.auth.service import AuthService
from .schemas import BudgetUpdate, UserRead, UserNameUpdate, UserPasswordUpdate
from .service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserRead)
def me(
    user_service: Annotated[UserService, Depends()],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
) -> UserRead:
    """Get current user with computed budget fields."""
    user_read = user_service.get_current_user(user_id)
    if not user_read:
        from fastapi import HTTPException
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return user_read


@router.patch("/me/budget", response_model=UserRead)
def update_budget(
    body: BudgetUpdate,
    user_service: Annotated[UserService, Depends()],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
):
    """Set or update the user's budget."""
    return user_service.update_budget(user_id, body.budget)


@router.delete("/me/budget", response_model=UserRead)
def delete_budget(
    user_service: Annotated[UserService, Depends()],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
):
    """Remove the user's budget (set to null)."""
    return user_service.delete_budget(user_id)


@router.patch("/me", response_model=UserRead)
def update_name(
    body: UserNameUpdate,
    user_service: Annotated[UserService, Depends()],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
):
    """Update the user's display name."""
    return user_service.update_name(user_id, body.name)


@router.delete("/me/name", response_model=UserRead)
def delete_name(
    user_service: Annotated[UserService, Depends()],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
):
    """Remove the user's display name (set to null)."""
    return user_service.delete_name(user_id)


@router.patch("/me/password", status_code=status.HTTP_204_NO_CONTENT)
def update_password(
    body: UserPasswordUpdate,
    response: Response,
    user_service: Annotated[UserService, Depends()],
    auth_service: Annotated[AuthService, Depends()],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
):
    """Update the user's password, log out every other device, keep this one logged in."""
    user_service.update_password(user_id, body.current_password, body.new_password)
    new_raw_refresh_token = auth_service.revoke_all_sessions_and_start_new_one(user_id)
    set_refresh_token_cookie(response, new_raw_refresh_token)
