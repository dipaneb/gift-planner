from typing import Annotated

from fastapi import APIRouter, Body, Cookie, Depends, Request, status, Response, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from src.config.settings import get_settings
from .service import AuthService
from .schemas import LoginData, UserCreate
from .router_examples import REGISTER_EXAMPLES
from .access_token_handler import create_access_token

settings = get_settings()

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
def signup_user(service: Annotated[AuthService, Depends()], user_create: Annotated[UserCreate, Body(openapi_examples=REGISTER_EXAMPLES)]):
    user = service.register_user(user_create)
    return {
        "success": True,
        "message": "",
        "data": {
            "id": user.id
        }
    }


@router.post("/login", response_model=LoginData, status_code=status.HTTP_200_OK)
def login(response: Response, auth_service: Annotated[AuthService, Depends()], form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    email = form_data.username # clarification because OAuth2PasswordRequestForm requires 'username'
    password = form_data.password

    access_token, refresh_token_raw, expires_in = auth_service.login(email, password)


    # Cookie refresh token (HttpOnly)
    response.set_cookie(
        key="refresh_token",
        value=refresh_token_raw,
        httponly=True,
        secure=(settings.ENV == "production"),
        samesite="strict",
        path="/auth",  # limits cookie sending to the refresh endpoint
        max_age=60 * 60 * 24 * 30,  # 30 days (should match refresh token TTL)
    )

    return LoginData(access_token=access_token, expires_in=expires_in)


@router.post("/refresh", response_model=LoginData)
def refresh(request: Request, response: Response, auth_service: Annotated[AuthService, Depends()]):
    old_raw_refresh_token = request.cookies.get("refresh_token")
    if not old_raw_refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    try:
        user_id, new_refresh_raw = auth_service.rotate(old_raw_refresh_token)
    except ValueError as e:
        # Deleting the cookie from client side eitherway.
        response.delete_cookie(key="refresh_token", path="/auth")
        if str(e) in {"refresh_reuse", "invalid_refresh", "refresh_expired"}:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
        raise

    access_token_lifespan_in_minutes = settings.ACCESS_TOKEN_LIFESPAN_IN_MINUTES
    new_access_token = create_access_token(subject=str(user_id), expires_minutes=access_token_lifespan_in_minutes)

    response.set_cookie(
        key="refresh_token",
        value=new_refresh_raw,
        httponly=True,
        secure=(settings.ENV == "production"),
        samesite="strict",
        path="/auth",  # limits cookie sending to the refresh endpoint
        max_age=60 * 60 * 24 * 30,  # 30 days (should match refresh token TTL)
    )

    return LoginData(
        access_token=new_access_token,
        expires_in=access_token_lifespan_in_minutes * 60,
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
# def logout(raw_refresh_token: Annotated[str | None, Cookie(alias="refresh_token")], response: Response, auth_service: Annotated[AuthService, Depends()]):
def logout(request: Request, response: Response, auth_service: Annotated[AuthService, Depends()]):
    raw_refresh_token = request.cookies.get("refresh_token")
    
    # always delete the cookie on client side, even when absent/invalid.
    response.delete_cookie(key="refresh_token", path="/auth")

    if not raw_refresh_token:
        return
    
    auth_service.global_logout(raw_refresh_token)
    return
