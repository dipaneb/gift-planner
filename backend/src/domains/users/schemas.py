# from __future__ import annotations

from uuid import UUID
from pydantic import BaseModel, ConfigDict, EmailStr


class UserRead(BaseModel):
    id: UUID
    email: EmailStr
    name: str | None

    model_config = ConfigDict(from_attributes=True)
