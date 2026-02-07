import uuid
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.domains.gifts.enums import GiftStatusEnum
from src.core.pagination import PaginationMeta

class GiftCreate(BaseModel):
    """Model for gift creation."""
    name: str = Field(max_length=255)
    url: str | None = Field(default=None, max_length=255, description="Optional URL to the gift")
    price: Decimal | None = Field(default=None, gt=0, decimal_places=2, description="Price in euros (minimum 9)")
    status: GiftStatusEnum = Field(default=GiftStatusEnum.idee, description="Gift status")
    quantity: int = Field(default=1, ge=1, description="Quantity (minimum 1)")
    recipient_ids: list[uuid.UUID] = Field(default_factory=list, description="List of recipient IDs to associate")

    @field_validator("name", mode="before")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        value = value.strip()
        if len(value) == 0:
            raise ValueError("Name cannot be empty nor only whitespaces.")
        return value

    @field_validator("url", mode="before")
    @classmethod
    def normalize_url(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        return value if value else None


class GiftUpdate(BaseModel):
    """Model for gift update (PATCH - all fields optional)."""
    name: str | None = Field(default=None, max_length=255)
    url: str | None = Field(default=None, max_length=255)
    price: Decimal | None = Field(default=None, gt=0, decimal_places=2)
    status: GiftStatusEnum | None = Field(default=None)
    quantity: int | None = Field(default=None, ge=1)
    recipient_ids: list[uuid.UUID] | None = Field(default=None, description="Replace associated recipients")

    @field_validator("name", mode="before")
    @classmethod
    def normalize_name(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        if len(value) == 0:
            raise ValueError("Name cannot be empty nor only whitespaces.")
        return value

    @field_validator("url", mode="before")
    @classmethod
    def normalize_url(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        return value if value else None


class GiftResponse(BaseModel):
    """Model for gift response."""
    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    url: str | None
    price: Decimal | None
    status: GiftStatusEnum
    quantity: int
    recipient_ids: list[uuid.UUID] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class PaginatedGiftsResponse(BaseModel):
    """Paginated response for gifts list."""
    items: list[GiftResponse]
    meta: PaginationMeta
