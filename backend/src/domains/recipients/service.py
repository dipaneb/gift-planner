from typing import Annotated
import uuid
import math

from fastapi import Depends, HTTPException, status

from src.core.pagination import PaginationMeta
from .models import Recipient
from .repository import RecipientRepository
from .schemas import RecipientUpdate, PaginatedRecipientsResponse, RecipientResponse
from src.domains.gifts.repository import GiftRepository


class RecipientService:
    def __init__(
        self,
        repo: Annotated[RecipientRepository, Depends()],
        gift_repo: Annotated[GiftRepository, Depends()],
    ):
        self.repo = repo
        self.gift_repo = gift_repo

    def _resolve_gifts(self, user_id: uuid.UUID, gift_ids: list[uuid.UUID]) -> list:
        """Resolve gift IDs to Gift objects, validating ownership."""
        gifts = []
        for gift_id in gift_ids:
            gift = self.gift_repo.get_by_id(user_id, gift_id)
            if not gift:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Gift {gift_id} not found"
                )
            gifts.append(gift)
        return gifts

    def _recipient_to_response(self, recipient: Recipient) -> RecipientResponse:
        """Convert a Recipient model to a RecipientResponse with gift_ids."""
        return RecipientResponse(
            id=recipient.id,
            user_id=recipient.user_id,
            name=recipient.name,
            notes=recipient.notes,
            gift_ids=[gift.id for gift in recipient.gifts],
        )

    def create(
        self,
        user_id: uuid.UUID,
        name: str,
        notes: str | None,
        gift_ids: list[uuid.UUID],
    ) -> RecipientResponse:
        gifts = self._resolve_gifts(user_id, gift_ids)

        new_recipient = Recipient(user_id=user_id, name=name, notes=notes)
        new_recipient.gifts = gifts

        created = self.repo.create(new_recipient)
        return self._recipient_to_response(created)

    def get(self, pagination: dict, user_id: uuid.UUID) -> PaginatedRecipientsResponse:
        page = pagination["page"]
        limit = pagination["limit"]
        
        recipients, total = self.repo.get(pagination, user_id)
        
        total_pages = math.ceil(total / limit) if total > 0 else 0
        
        meta = PaginationMeta(
            page=page,
            limit=limit,
            total=total,
            totalPages=total_pages,
            hasPrev=page > 1,
            hasNext=page < total_pages
        )
        
        return PaginatedRecipientsResponse(
            items=[self._recipient_to_response(r) for r in recipients],
            meta=meta
        )

    def get_by_id(self, user_id: uuid.UUID, recipient_id: uuid.UUID) -> RecipientResponse:
        """
        Get recipient by ID. Raises 404 if not found or doesn't belong to user.
        """
        recipient = self.repo.get_by_id(user_id, recipient_id)
        if not recipient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recipient not found"
            )
        return self._recipient_to_response(recipient)

    def update(self, user_id: uuid.UUID, recipient_id: uuid.UUID, update_data: RecipientUpdate) -> RecipientResponse:
        """
        Update recipient. Raises 404 if not found or doesn't belong to user.
        """
        recipient = self.repo.get_by_id(user_id, recipient_id)
        if not recipient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recipient not found"
            )

        update_dict = update_data.model_dump(exclude_unset=True)

        # Handle gift_ids separately
        gift_ids = update_dict.pop("gift_ids", None)
        if gift_ids is not None:
            recipient.gifts = self._resolve_gifts(user_id, gift_ids)

        # Update only provided fields
        for field, value in update_dict.items():
            setattr(recipient, field, value)
        
        updated = self.repo.update(recipient)
        return self._recipient_to_response(updated)

    def delete(self, user_id: uuid.UUID, recipient_id: uuid.UUID) -> None:
        """
        Delete recipient. Raises 404 if not found or doesn't belong to user.
        """
        deleted = self.repo.delete(user_id, recipient_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recipient not found"
            )