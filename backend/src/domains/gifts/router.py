from typing import Annotated
import uuid

from fastapi import APIRouter, Body, Depends, status

from src.core.pagination import PaginationDeps
from src.domains.auth.dependencies import get_current_user_id
from .service import GiftService
from .schemas import GiftCreate, GiftUpdate, GiftResponse, PaginatedGiftsResponse
from .router_examples import CREATE_GIFT_EXAMPLE, UPDATE_GIFT_EXAMPLE

router = APIRouter(prefix="/gifts", tags=["gifts"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=GiftResponse)
def create_gift(
    new_gift: Annotated[GiftCreate, Body(openapi_examples=CREATE_GIFT_EXAMPLE)],
    gift_service: Annotated[GiftService, Depends()],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
):
    """Create a new gift."""
    return gift_service.create(
        user_id=user_id,
        name=new_gift.name,
        url=new_gift.url,
        price=new_gift.price,
        status_val=new_gift.status,
        quantity=new_gift.quantity,
        recipient_ids=new_gift.recipient_ids,
    )


@router.get("", response_model=PaginatedGiftsResponse)
def get_gifts(
    pagination: PaginationDeps,
    gift_service: Annotated[GiftService, Depends()],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
):
    """Get all gifts for the authenticated user with pagination."""
    return gift_service.get(pagination, user_id)


@router.get("/{gift_id}", response_model=GiftResponse)
def get_gift(
    gift_id: uuid.UUID,
    gift_service: Annotated[GiftService, Depends()],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
):
    """Get a specific gift by ID."""
    return gift_service.get_by_id(user_id, gift_id)


@router.patch("/{gift_id}", response_model=GiftResponse)
def update_gift(
    gift_id: uuid.UUID,
    update_data: Annotated[GiftUpdate, Body(openapi_examples=UPDATE_GIFT_EXAMPLE)],
    gift_service: Annotated[GiftService, Depends()],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
):
    """Update a gift (partial update)."""
    return gift_service.update(user_id, gift_id, update_data)


@router.delete("/{gift_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_gift(
    gift_id: uuid.UUID,
    gift_service: Annotated[GiftService, Depends()],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
):
    """Delete a gift."""
    gift_service.delete(user_id, gift_id)
