from typing import Annotated
import uuid
import math
from decimal import Decimal

from fastapi import Depends, HTTPException, status

from src.core.pagination import PaginationMeta
from .models import Gift
from .repository import GiftRepository
from .schemas import GiftUpdate, PaginatedGiftsResponse, GiftResponse
from src.domains.recipients.repository import RecipientRepository


class GiftService:
    def __init__(
        self,
        repo: Annotated[GiftRepository, Depends()],
        recipient_repo: Annotated[RecipientRepository, Depends()],
    ):
        self.repo = repo
        self.recipient_repo = recipient_repo

    def _resolve_recipients(self, user_id: uuid.UUID, recipient_ids: list[uuid.UUID]) -> list:
        """Resolve recipient IDs to Recipient objects, validating ownership."""
        recipients = []
        for recipient_id in recipient_ids:
            recipient = self.recipient_repo.get_by_id(user_id, recipient_id)
            if not recipient:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Recipient {recipient_id} not found"
                )
            recipients.append(recipient)
        return recipients

    def _gift_to_response(self, gift: Gift) -> GiftResponse:
        """Convert a Gift model to a GiftResponse with recipient_ids."""
        return GiftResponse(
            id=gift.id,
            user_id=gift.user_id,
            name=gift.name,
            url=gift.url,
            price=gift.price,
            status=gift.status,
            quantity=gift.quantity,
            recipient_ids=[recipient.id for recipient in gift.recipients],
        )

    def create(
        self,
        user_id: uuid.UUID,
        name: str,
        url: str | None,
        price: Decimal | None,
        status_val: str,
        quantity: int,
        recipient_ids: list[uuid.UUID],
    ) -> GiftResponse:
        recipients = self._resolve_recipients(user_id, recipient_ids)

        new_gift = Gift(
            user_id=user_id,
            name=name,
            url=url,
            price=price,
            status=status_val,
            quantity=quantity,
        )
        new_gift.recipients = recipients

        created = self.repo.create(new_gift)
        return self._gift_to_response(created)

    def get(self, pagination: dict, user_id: uuid.UUID) -> PaginatedGiftsResponse:
        page = pagination["page"]
        limit = pagination["limit"]

        gifts, total = self.repo.get(pagination, user_id)

        total_pages = math.ceil(total / limit) if total > 0 else 0

        meta = PaginationMeta(
            page=page,
            limit=limit,
            total=total,
            totalPages=total_pages,
            hasPrev=page > 1,
            hasNext=page < total_pages
        )

        return PaginatedGiftsResponse(
            items=[self._gift_to_response(g) for g in gifts],
            meta=meta
        )

    def get_by_id(self, user_id: uuid.UUID, gift_id: uuid.UUID) -> GiftResponse:
        """
        Get gift by ID. Raises 404 if not found or doesn't belong to user.
        """
        gift = self.repo.get_by_id(user_id, gift_id)
        if not gift:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Gift not found"
            )
        return self._gift_to_response(gift)

    def update(self, user_id: uuid.UUID, gift_id: uuid.UUID, update_data: GiftUpdate) -> GiftResponse:
        """
        Update gift. Raises 404 if not found or doesn't belong to user.
        """
        gift = self.repo.get_by_id(user_id, gift_id)
        if not gift:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Gift not found"
            )

        update_dict = update_data.model_dump(exclude_unset=True)

        # Handle recipient_ids separately
        recipient_ids = update_dict.pop("recipient_ids", None)
        if recipient_ids is not None:
            gift.recipients = self._resolve_recipients(user_id, recipient_ids)

        # Update only provided fields
        for field, value in update_dict.items():
            setattr(gift, field, value)

        updated = self.repo.update(gift)
        return self._gift_to_response(updated)

    def delete(self, user_id: uuid.UUID, gift_id: uuid.UUID) -> None:
        """
        Delete gift. Raises 404 if not found or doesn't belong to user.
        """
        deleted = self.repo.delete(user_id, gift_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Gift not found"
            )
