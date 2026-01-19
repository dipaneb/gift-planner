from typing import Annotated
import uuid
from datetime import datetime, timezone, timedelta

from fastapi import Depends, HTTPException, status

from src.config.settings import get_settings
from src.domains.users.repository import UserRepository
from src.domains.users.models import User
from .repository import RefreshTokenRepository
from .models import RefreshToken
from .schemas import UserCreate
from .password_handler import get_password_hash, verify_password
from .access_token_handler import create_access_token
from .refresh_token_handler import hash_token, get_refresh_token_fingerprint, verify_refresh_token


settings = get_settings()


class AuthService:
    def __init__(self, user_repo: Annotated[UserRepository, Depends()], refresh_token_repo: Annotated[RefreshTokenRepository, Depends()]):
        self.user_repo = user_repo
        self.refresh_token_repo = refresh_token_repo
        

    def register_user(self, user_create: UserCreate) -> User:
        # check email uniqueness
        existing = self.user_repo.get_by_email(user_create.email)
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already in use.")

        hashed_password = get_password_hash(user_create.password)  
        user = User(email=user_create.email, name=user_create.name, password_hash=hashed_password)
        return self.user_repo.create(user)

    def login(self, email: str, password: str) -> tuple[str, str, int]:
        """
        Return (access_token, refresh_token_raw, expires_in_seconds)
        """
        normalized_email = email.lower()
        user = self.user_repo.get_by_email(normalized_email)

        # Prevent enumeration by raising the same error if user is absent or password is false.
        if not user or not verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token_lifespan_in_minutes = settings.ACCESS_TOKEN_LIFESPAN_IN_MINUTES
        access_token = create_access_token(
            subject=str(user.id),
            expires_minutes=access_token_lifespan_in_minutes,
        )

        raw_refresh_token = self.__create_refresh_token_for_user(user.id)

        expires_in_seconds = access_token_lifespan_in_minutes * 60
        return access_token, raw_refresh_token, expires_in_seconds
    

    def rotate(self, old_raw_refresh_token: str) -> tuple[uuid.UUID, str]:
        """
        Returns (user_id, new_raw_refresh_token)
        If a reused token is detected, all the refresh tokens for the user are deleted.
        """
        # Getting the old refresh token entity from database
        old_refresh_token_fingerprint = get_refresh_token_fingerprint(old_raw_refresh_token)
        token = self.refresh_token_repo.get_by_fingerprint(old_refresh_token_fingerprint)

        if token is None:
            raise ValueError("invalid_refresh")
        
        # If refresh token already revoked => possible reuse => cyberattack or concurent refresh
        if token.revoked_at is not None:
            self.refresh_token_repo.delete_all_for_user(token.user_id)
            raise ValueError("refresh_reuse")
        
        # Expired
        now = datetime.now(timezone.utc)
        expires_at_aware = token.expires_at.replace(tzinfo=timezone.utc) if token.expires_at.tzinfo is None else token.expires_at
        if expires_at_aware <= now:
            raise ValueError("invalid_refresh")
        

        # Check for old_raw_refresh_token validity
        if not verify_refresh_token(old_raw_refresh_token, token.token_hash):
            raise ValueError("invalid_refresh")
        
        # Rotation: create new token and invalidate former one
        new_raw_refresh_token = self.__create_refresh_token_for_user(token.user_id)

        # We want to store replaced_by_id, so the new id has to be known.
        # But since __create_refresh_token_for_user() doesn't return the object,
        # we lookup for the new refresh token via fingerprint.
        new_refresh_token_fingerprint = get_refresh_token_fingerprint(new_raw_refresh_token)
        new_refresh_token = self.refresh_token_repo.get_by_fingerprint(new_refresh_token_fingerprint)
        if new_refresh_token is None: # unlikely but better to be safe than sorry.
            raise RuntimeError("refresh_rotation_failed")
        
        self.refresh_token_repo.revoke(token.id, replaced_by_id=new_refresh_token.id)

        return token.user_id, new_raw_refresh_token


    def __create_refresh_token_for_user(self, user_id: uuid.UUID) -> str:
        raw_token = uuid.uuid4().hex
        refresh_token_fingerprint = get_refresh_token_fingerprint(raw_token)
        token_hash = hash_token(raw_token)

        expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_TTL_DAYS)

        token = RefreshToken(
            user_id=user_id,
            token_fingerprint=refresh_token_fingerprint,
            token_hash=token_hash,
            expires_at=expires_at,
        )

        self.refresh_token_repo.create(token)

        # IMPORTANT : the plain token is return ONE TIME ONLY
        return raw_token

