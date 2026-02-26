import re
import uuid
from decimal import Decimal

from typing_extensions import Self
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator


class UserRead(BaseModel):
    id: uuid.UUID
    email: EmailStr
    name: str | None
    budget: Decimal | None
    spent: Decimal
    remaining: Decimal | None

    model_config = ConfigDict(from_attributes=True)


class BudgetUpdate(BaseModel):
    budget: Decimal = Field(gt=0, decimal_places=2, description="Budget in euros (must be positive)")


class UserNameUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=255, description="User's display name")


class UserPasswordUpdate(BaseModel):
    current_password: str = Field(min_length=1, description="Current password for verification")
    new_password: str = Field(min_length=8, max_length=255, description="Password must contain at least one uppercase letter, one lowercase letter, one digit, and one special character.")
    confirmed_password: str = Field(min_length=8, max_length=255, description="Confirmation of new password")

    @field_validator("new_password")
    @classmethod
    def validate_password_strength(cls, password: str) -> str:
        if not re.search(r"[A-Z]", password):
            raise ValueError("Password must contain at least one uppercase letter.")
        if not re.search(r"[a-z]", password):
            raise ValueError("Password must contain at least one lowercase letter.")
        if not re.search(r"\d", password):
            raise ValueError("Password must contain at least one digit.")
        if not re.search(r"[^A-Za-z0-9\s]", password):
            raise ValueError("Password must contain at least one special character.")
        return password

    @model_validator(mode="after")
    def check_passwords_match(self) -> Self:
        if self.new_password != self.confirmed_password:
            raise ValueError("Password and confirm password do not match.")
        return self