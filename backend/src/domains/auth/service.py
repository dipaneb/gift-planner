from typing import Annotated

from fastapi import Depends, HTTPException, status

from .repository import UserRepository
from .schemas import UserCreate
from src.domains.users.models import User
from .password_handler import get_password_hash

class UserService:
    def __init__(self, repo: Annotated[UserRepository, Depends()]):
        self.repo = repo
    
    def register_user(self, user_create: UserCreate) -> User:
        # check email uniqueness
        existing = self.repo.get_by_email(user_create.email)
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already in use.")

        hashed_password = get_password_hash(user_create.password)  
        user = User(email=user_create.email, name=user_create.name, password_hash=hashed_password)
        return self.repo.create(user)
