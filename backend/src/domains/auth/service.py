from typing import Annotated
import uuid
from datetime import datetime, timezone, timedelta

from fastapi import Depends, HTTPException, status

from .schemas import UserCreate
from src.domains.users.repository import UserRepository
from src.domains.users.models import User
from .password_handler import get_password_hash, verify_password

from src.config.settings import get_settings
from src.domains.auth.jwt_handler import create_access_token
from src.domains.auth.password_handler import verify_password
from src.domains.users.repository import UserRepository
from src.domains.auth.repository import RefreshTokenRepository
from src.domains.auth.models import RefreshToken
from .refresh_token_handler import hash_token

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

        raw_refresh_token = self.__create_for_user(user.id)

        expires_in_seconds = access_token_lifespan_in_minutes * 60
        return access_token, raw_refresh_token, expires_in_seconds
    
    def __create_for_user(self, user_id: uuid.UUID) -> str:
        raw_token = uuid.uuid4().hex
        token_hash = hash_token(raw_token)

        expires_at = datetime.now(timezone.utc) + timedelta(
            days=settings.REFRESH_TOKEN_TTL_DAYS
        )

        token = RefreshToken(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
        )

        self.refresh_token_repo.create(token)

        # IMPORTANT : the plain token is return ONE TIME ONLY
        return raw_token

