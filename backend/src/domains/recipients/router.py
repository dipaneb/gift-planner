from typing import Annotated
import uuid

from fastapi import APIRouter, Body, Depends, status

from src.core.pagination import PaginationDeps
from src.domains.auth.dependencies import get_current_user_id
from .service import RecipientService
from .schemas import RecipientCreate, RecipientUpdate, RecipientResponse
from .router_examples import CREATE_RECIPIENT_EXAMPLE, UPDATE_RECIPIENT_EXAMPLE

router = APIRouter(prefix="/recipients", tags=["recipients"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=RecipientResponse)
def create_recipient(
    new_recipient: Annotated[RecipientCreate, Body(openapi_examples=CREATE_RECIPIENT_EXAMPLE)],
    recipient_service: Annotated[RecipientService, Depends()],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
):
    """Create a new recipient."""
    return recipient_service.create(
        user_id=user_id,
        name=new_recipient.name,
        notes=new_recipient.notes
    )


@router.get("", response_model=list[RecipientResponse])
def get_recipients(
    pagination: PaginationDeps,
    recipient_service: Annotated[RecipientService, Depends()],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
):
    """Get all recipients for the authenticated user with pagination."""
    return recipient_service.get(pagination, user_id)


@router.get("/{recipient_id}", response_model=RecipientResponse)
def get_recipient(
    recipient_id: uuid.UUID,
    recipient_service: Annotated[RecipientService, Depends()],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
):
    """Get a specific recipient by ID."""
    return recipient_service.get_by_id(user_id, recipient_id)


@router.patch("/{recipient_id}", response_model=RecipientResponse)
def update_recipient(
    recipient_id: uuid.UUID,
    update_data: Annotated[RecipientUpdate, Body(openapi_examples=UPDATE_RECIPIENT_EXAMPLE)],
    recipient_service: Annotated[RecipientService, Depends()],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
):
    """Update a recipient (partial update)."""
    return recipient_service.update(user_id, recipient_id, update_data)


@router.delete("/{recipient_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_recipient(
    recipient_id: uuid.UUID,
    recipient_service: Annotated[RecipientService, Depends()],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
):
    """Delete a recipient."""
    recipient_service.delete(user_id, recipient_id)