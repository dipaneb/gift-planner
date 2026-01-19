from typing import Annotated

from fastapi import APIRouter, Body, Depends, status, Response
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer

from src.config.settings import get_settings
from .service import AuthService
from .schemas import LoginData, UserCreate
from .router_examples import REGISTER_EXAMPLES

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
        path="/auth/refresh",  # limits cookie sending to the refresh endpoint
        max_age=60 * 60 * 24 * 30,  # 30 days (should match refresh token TTL)
    )

    return LoginData(access_token=access_token, expires_in=expires_in)

