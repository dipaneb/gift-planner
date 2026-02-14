import uuid
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


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
