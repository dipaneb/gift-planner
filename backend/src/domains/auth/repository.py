from typing import Annotated
from datetime import datetime, timezone

from fastapi import Depends
from sqlalchemy import select, update, delete
from sqlalchemy.orm import Session

from src.infrastructure.database.session import get_db
from .models import RefreshToken, PasswordResetToken


class RefreshTokenRepository:
    def __init__(self, db: Annotated[Session, Depends(get_db)]):
        self.db = db

    def create(self, token: RefreshToken) -> RefreshToken:
        self.db.add(token)
        self.db.commit()
        self.db.refresh(token)
        return token

    def get_by_fingerprint(self, fingerprint: str) -> RefreshToken | None:
        stmt = select(RefreshToken).where(RefreshToken.token_fingerprint == fingerprint)
        return self.db.execute(stmt).scalar_one_or_none()
    
    def revoke(self, token_id, *, replaced_by_id=None) -> None:
        now = datetime.now(timezone.utc)
        stmt = update(RefreshToken).where(RefreshToken.id == token_id).values(revoked_at=now, replaced_by_id=replaced_by_id)
        self.db.execute(stmt)
        self.db.commit()
    
    def delete_all_tokens_for_user(self, user_id) -> None:
        stmt = delete(RefreshToken).where(RefreshToken.user_id == user_id)
        self.db.execute(stmt)
        self.db.commit()


class ResetPasswordRepository:
    def __init__(self, db: Annotated[Session, Depends(get_db)]):
        self.db = db

    def create(self, password_reset_token: PasswordResetToken) -> PasswordResetToken:
        self.db.add(password_reset_token)
        self.db.commit()
        self.db.refresh(password_reset_token)
        return password_reset_token