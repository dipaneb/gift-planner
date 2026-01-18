from uuid import uuid4
from typing_extensions import Self
import re

from pydantic import BaseModel, EmailStr, Field, model_validator, field_validator


class UserCreate(BaseModel):
    """Model for user registration."""
    email: EmailStr
    password: str = Field(min_length=8, max_length=255, description="Password must contain at least one uppercase letter, one lowercase letter, one digit, and one special character.")
    confirmed_password: str = Field(min_length=8, max_length=255)
    name: str | None = Field(default=None, max_length=255, description="Optional display name")

    @field_validator("email", mode="after")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        """
        Even though pydantic EmailStr type already lower the domain part of the email address,
        it does not affect the local part (the part before the '@' symbol).
        This is probably because, by the RFC 5321, part 2.4,
        the local part should be case-sensitive but the domain part should be insensitive.
        In practice, major providers like gmail or outlook,
        treat the local part as case-insensitive which is also the approach taken on this project.
        """
        return value.lower()

    @field_validator("name", mode="before")
    @classmethod
    def normalize_name(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        return value if value else None


    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, password: str) -> str:
        """
        Enforce password complexity rules.
        For complex and upgradeable regex, prefer field_validator to regex parameter on Field.
        field_validator offers better scalabilty and better legibilty in code and error messages.
        """
        if not re.search(r"[A-Z]", password):
            raise ValueError("Password must contain at least one uppercase letter.")
        if not re.search(r"[a-z]", password):
            raise ValueError("Password must contain at least one lowercase letter.")
        if not re.search(r"\d", password):
            raise ValueError("Password must contain at least one digit.")
        if not re.search(r"[^\w\s]", password):
            raise ValueError("Password must contain at least one special character.")
        return password
    
    @model_validator(mode="after")
    def check_passwords_match(self) -> Self:
        if self.password != self.confirmed_password:
            raise ValueError("Password and confirm password do not match.")
        return self
    