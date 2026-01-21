# from __future__ import annotations

import uuid
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from src.config.settings import get_settings
from src.domains.users.repository import UserRepository
from src.domains.users.models import User

settings = get_settings()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def _unauthorized() -> HTTPException:
    """
    Using a function is better than a variable (_unauthorized=HTTPException(detail="..."))
    Indeed, a function create a new instance every time it is called.
    Where a variable would be a unique instance shared everywhere it is used.
    Which mean that changing a instance attribute would change it everywhere (e.g. _unauthorized.detail="...").

    """
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user_id(token: Annotated[str, Depends(oauth2_scheme)]) -> uuid.UUID:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        sub = payload.get("sub")
        if not sub:
            raise ValueError("Missing sub")
        return uuid.UUID(sub)
    except Exception:
        raise _unauthorized()


def get_current_user(user_id: Annotated[uuid.UUID, Depends(get_current_user_id)], user_repo: Annotated[UserRepository, Depends()]) -> User:
    user = user_repo.get_by_id(user_id)
    if user is None:
        raise _unauthorized()
    return user
