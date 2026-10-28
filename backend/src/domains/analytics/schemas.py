import uuid

from pydantic import BaseModel, Field


class VisitCreate(BaseModel):
    """Model for recording a visit (sent once per browser session by the frontend)."""
    from_cv: bool = Field(default=False, description="True if the visitor came from the CV link")
    visitor_id: uuid.UUID = Field(description="Random id persisted in the visitor's browser")
