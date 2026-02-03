from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Body, Depends, Query, Request, status, Response, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr

from src.config.settings import get_settings
from .service import AuthService
from .schemas import LoginData, UserCreate, UserUpdatePartial
from .router_examples import REGISTER_EXAMPLES, RESET_PASSWORD_EXAMPLE
from .access_token_handler import create_access_token
from src.infrastructure.external_services.email_service import MailJetClient

settings = get_settings()

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=LoginData)
def signup_user(response: Response, service: Annotated[AuthService, Depends()], user_create: Annotated[UserCreate, Body(openapi_examples=REGISTER_EXAMPLES)]):
    service.register_user(user_create)
    
    # Automatically log in the user after registration by calling the login endpoint
    form_data = OAuth2PasswordRequestForm(username=user_create.email, password=user_create.password)
    return login(response, service, form_data)


@router.post("/login", response_model=LoginData)
def login(response: Response, auth_service: Annotated[AuthService, Depends()], form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    email = form_data.username # clarification because OAuth2PasswordRequestForm requires 'username'
    password = form_data.password

    access_token, refresh_token_raw, expires_in, user = auth_service.login(email, password)

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

    return LoginData(access_token=access_token, expires_in=expires_in, user=user)


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

    user = auth_service.user_repo.get_by_id(user_id)
    if not user:
        response.delete_cookie(key="refresh_token", path="/auth")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

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
        user=user,
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(request: Request, response: Response, auth_service: Annotated[AuthService, Depends()]):
    raw_refresh_token = request.cookies.get("refresh_token")
    
    # always delete the cookie on client side, even when absent/invalid.
    response.delete_cookie(key="refresh_token", path="/auth")

    if not raw_refresh_token:
        return
    
    auth_service.global_logout(raw_refresh_token)
    return


@router.post("/forgot-password")
def send_email_for_forgot_password(email: Annotated[EmailStr, Body(embed=True)], auth_service: Annotated[AuthService, Depends()], background_tasks: BackgroundTasks):
    email_job = auth_service.request_reset(email)

    if email_job:
        mailjet_client = MailJetClient(settings.MAILJET_API_KEY, settings.MAILJET_API_SECRET_KEY)
        background_tasks.add_task(
            mailjet_client.send_email,
            from_email=settings.MAIL_FROM_EMAIL,
            from_name=settings.MAIL_FROM_NAME,
            to_email=email_job["to_email"],
            to_name=email_job["to_name"],
            subject=email_job["subject"],
            html=email_job["html"],
            text=email_job["text"],
        )

    # Always send the same response to avoid email enumeration.
    return {
        "success": True,
        "message": "If the email exists, a reset link was sent."
    }


@router.post("/reset-password")
def reset_password(reset_password_token: Annotated[str, Query(alias="token")], body: Annotated[UserUpdatePartial, Body(openapi_examples=RESET_PASSWORD_EXAMPLE)], auth_service: Annotated[AuthService, Depends()]):
    try:
        auth_service.reset_password(reset_password_token, body.password)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token")
    
    return {"success": True, "message": "Password updated."}
