from typing import Annotated
from fastapi import APIRouter, Body, Depends, status

from .service import UserService
from .schemas import UserCreate
from .router_examples import REGISTER_EXAMPLES

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
def signup_user(service: Annotated[UserService, Depends()], user_create: Annotated[UserCreate, Body(openapi_examples=REGISTER_EXAMPLES)]):
    user = service.register_user(user_create)
    return {
        "success": True,
        "message": "",
        "data": {
            "id": user.id
        }
    }