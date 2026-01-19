from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from src.infrastructure.database.session import get_db
from .models import RefreshToken


class RefreshTokenRepository:
    def __init__(self, db: Annotated[Session, Depends(get_db)]):
        self.db = db

    def create(self, token: RefreshToken) -> RefreshToken:
        self.db.add(token)
        self.db.commit()
        self.db.refresh(token)
        return token
