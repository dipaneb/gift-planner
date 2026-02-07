import uuid

from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.core.pagination import PaginationMeta

class RecipientCreate(BaseModel):
    """Model for recipient creation."""
    name: str = Field(max_length=255)
    notes: str | None = Field(default=None, max_length=6000, description="Optional notes")

    @field_validator("name", mode="before")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        value = value.strip()
        if len(value) == 0:
            raise ValueError("Name cannot be empty nor only whitespaces.")
        return value

    @field_validator("notes", mode="before")
    @classmethod
    def normalize_notes(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        return value if value else None


class RecipientUpdate(BaseModel):
    """Model for recipient update (PATCH - all fields optional)."""
    name: str | None = Field(default=None, max_length=255)
    notes: str | None = Field(default=None, max_length=6000, description="Optional notes")

    @field_validator("name", mode="before")
    @classmethod
    def normalize_name(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        if len(value) == 0:
            raise ValueError("Name cannot be empty nor only whitespaces.")
        return value

    @field_validator("notes", mode="before")
    @classmethod
    def normalize_notes(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        return value if value else None


class RecipientResponse(BaseModel):
    """Model for recipient response."""
    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    notes: str | None


    model_config = ConfigDict(from_attributes=True)


class PaginatedRecipientsResponse(BaseModel):
    """Paginated response for recipients list."""
    items: list[RecipientResponse]
    meta: PaginationMeta
