import uuid
from pydantic import BaseModel, ConfigDict, EmailStr


class UserRead(BaseModel):
    id: uuid.UUID
    email: EmailStr
    name: str | None

    model_config = ConfigDict(from_attributes=True)
