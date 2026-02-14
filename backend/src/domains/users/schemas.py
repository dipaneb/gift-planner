import uuid
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator


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
    new_password: str = Field(min_length=8, description="New password (minimum 8 characters)")
    confirmed_password: str = Field(min_length=8, description="Confirmation of new password")

    @model_validator(mode="after")
    def check_passwords_match(self) -> Self:
        if self.new_password != self.confirmed_password:
            raise ValueError("Password and confirm password do not match.")
        return self