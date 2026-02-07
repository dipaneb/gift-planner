from typing import Annotated
import uuid
import math

from fastapi import Depends, HTTPException, status

from src.core.pagination import PaginationMeta
from .models import Recipient
from .repository import RecipientRepository
from .schemas import RecipientUpdate, PaginatedRecipientsResponse, RecipientResponse


class RecipientService:
    def __init__(self, repo: Annotated[RecipientRepository, Depends()]):
        self.repo = repo

    def create(self, user_id: uuid.UUID, name: str, notes: str | None) -> Recipient:
        new_recipient = Recipient(user_id=user_id, name=name, notes=notes)
        return self.repo.create(new_recipient)

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
            items=[RecipientResponse.model_validate(r) for r in recipients],
            meta=meta
        )

    def get_by_id(self, user_id: uuid.UUID, recipient_id: uuid.UUID) -> Recipient:
        """
        Get recipient by ID. Raises 404 if not found or doesn't belong to user.
        """
        recipient = self.repo.get_by_id(user_id, recipient_id)
        if not recipient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recipient not found"
            )
        return recipient

    def update(self, user_id: uuid.UUID, recipient_id: uuid.UUID, update_data: RecipientUpdate) -> Recipient:
        """
        Update recipient. Raises 404 if not found or doesn't belong to user.
        """
        recipient = self.get_by_id(user_id, recipient_id)
        
        # Update only provided fields
        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(recipient, field, value)
        
        return self.repo.update(recipient)

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