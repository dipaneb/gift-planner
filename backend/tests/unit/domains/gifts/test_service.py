import pytest
import uuid
from decimal import Decimal
from unittest.mock import Mock
from fastapi import HTTPException

from src.domains.gifts.service import GiftService
from src.domains.gifts.models import Gift
from src.domains.gifts.enums import GiftStatusEnum
from src.domains.gifts.schemas import GiftUpdate
from src.domains.recipients.models import Recipient


def _make_gift(user_id=None, gift_id=None, name="Test Gift", recipients=None, **kwargs):
    """Helper to build a Gift with sensible defaults."""
    gift = Gift(
        id=gift_id or uuid.uuid4(),
        user_id=user_id or uuid.uuid4(),
        name=name,
        url=kwargs.get("url"),
        price=kwargs.get("price"),
        status=kwargs.get("status", GiftStatusEnum.idee),
        quantity=kwargs.get("quantity", 1),
    )
    gift.recipients = recipients or []
    return gift


def _make_recipient(user_id, recipient_id=None, name="Recipient"):
    r = Recipient(id=recipient_id or uuid.uuid4(), user_id=user_id, name=name, notes=None)
    return r


class TestGiftServiceCreate:

    def test_create_gift_success(self):
        mock_repo = Mock()
        mock_recipient_repo = Mock()
        service = GiftService(mock_repo, mock_recipient_repo)

        user_id = uuid.uuid4()
        expected = _make_gift(user_id=user_id, name="Chess set")
        mock_repo.create.return_value = expected

        result = service.create(
            user_id=user_id,
            name="Chess set",
            url=None,
            price=None,
            status_val=GiftStatusEnum.idee,
            quantity=1,
            recipient_ids=[],
        )

        assert result.name == "Chess set"
        mock_repo.create.assert_called_once()

    def test_create_gift_with_recipients(self):
        mock_repo = Mock()
        mock_recipient_repo = Mock()
        service = GiftService(mock_repo, mock_recipient_repo)

        user_id = uuid.uuid4()
        rid = uuid.uuid4()
        recipient = _make_recipient(user_id, rid)
        mock_recipient_repo.get_by_id.return_value = recipient

        expected = _make_gift(user_id=user_id, name="Gift", recipients=[recipient])
        mock_repo.create.return_value = expected

        result = service.create(
            user_id=user_id,
            name="Gift",
            url=None,
            price=None,
            status_val=GiftStatusEnum.idee,
            quantity=1,
            recipient_ids=[rid],
        )

        assert result.recipient_ids == [rid]
        mock_recipient_repo.get_by_id.assert_called_once_with(user_id, rid)

    def test_create_gift_with_invalid_recipient_raises_404(self):
        mock_repo = Mock()
        mock_recipient_repo = Mock()
        service = GiftService(mock_repo, mock_recipient_repo)

        user_id = uuid.uuid4()
        rid = uuid.uuid4()
        mock_recipient_repo.get_by_id.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            service.create(
                user_id=user_id,
                name="Gift",
                url=None,
                price=None,
                status_val=GiftStatusEnum.idee,
                quantity=1,
                recipient_ids=[rid],
            )

        assert exc_info.value.status_code == 404
        mock_repo.create.assert_not_called()


class TestGiftServiceGet:

    def test_get_gifts_success(self):
        mock_repo = Mock()
        mock_recipient_repo = Mock()
        service = GiftService(mock_repo, mock_recipient_repo)

        user_id = uuid.uuid4()
        pagination = {"sort": "asc", "page": 1, "limit": 10}

        gifts = [
            _make_gift(user_id=user_id, name="Gift 1"),
            _make_gift(user_id=user_id, name="Gift 2"),
        ]
        mock_repo.get.return_value = (gifts, 2)

        result = service.get(pagination, user_id)

        assert len(result.items) == 2
        assert result.meta.total == 2
        assert result.meta.page == 1
        mock_repo.get.assert_called_once_with(pagination, user_id)

    def test_get_gifts_empty_list(self):
        mock_repo = Mock()
        mock_recipient_repo = Mock()
        service = GiftService(mock_repo, mock_recipient_repo)

        user_id = uuid.uuid4()
        pagination = {"sort": "default", "page": 1, "limit": 10}

        mock_repo.get.return_value = ([], 0)

        result = service.get(pagination, user_id)

        assert result.items == []
        assert result.meta.total == 0
        assert result.meta.totalPages == 0

    def test_get_gifts_pagination_meta(self):
        mock_repo = Mock()
        mock_recipient_repo = Mock()
        service = GiftService(mock_repo, mock_recipient_repo)

        user_id = uuid.uuid4()
        pagination = {"sort": "default", "page": 2, "limit": 2}

        gifts = [
            _make_gift(user_id=user_id, name="Gift 2"),
            _make_gift(user_id=user_id, name="Gift 3"),
        ]
        mock_repo.get.return_value = (gifts, 5)

        result = service.get(pagination, user_id)

        assert result.meta.page == 2
        assert result.meta.limit == 2
        assert result.meta.total == 5
        assert result.meta.totalPages == 3
        assert result.meta.hasPrev is True
        assert result.meta.hasNext is True


class TestGiftServiceGetById:

    def test_get_by_id_success(self):
        mock_repo = Mock()
        mock_recipient_repo = Mock()
        service = GiftService(mock_repo, mock_recipient_repo)

        user_id = uuid.uuid4()
        gift_id = uuid.uuid4()

        expected = _make_gift(user_id=user_id, gift_id=gift_id, name="Test Gift")
        mock_repo.get_by_id.return_value = expected

        result = service.get_by_id(user_id, gift_id)

        assert result.id == gift_id
        assert result.name == "Test Gift"
        mock_repo.get_by_id.assert_called_once_with(user_id, gift_id)

    def test_get_by_id_not_found_raises_404(self):
        mock_repo = Mock()
        mock_recipient_repo = Mock()
        service = GiftService(mock_repo, mock_recipient_repo)

        user_id = uuid.uuid4()
        gift_id = uuid.uuid4()

        mock_repo.get_by_id.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            service.get_by_id(user_id, gift_id)

        assert exc_info.value.status_code == 404
        assert "not found" in exc_info.value.detail.lower()


class TestGiftServiceUpdate:

    def test_update_gift_name_only(self):
        mock_repo = Mock()
        mock_recipient_repo = Mock()
        service = GiftService(mock_repo, mock_recipient_repo)

        user_id = uuid.uuid4()
        gift_id = uuid.uuid4()

        existing = _make_gift(user_id=user_id, gift_id=gift_id, name="Original")
        mock_repo.get_by_id.return_value = existing
        mock_repo.update.return_value = existing

        update_data = GiftUpdate(name="Updated Name")

        result = service.update(user_id, gift_id, update_data)

        assert result.name == "Updated Name"
        mock_repo.update.assert_called_once_with(existing)

    def test_update_gift_status(self):
        mock_repo = Mock()
        mock_recipient_repo = Mock()
        service = GiftService(mock_repo, mock_recipient_repo)

        user_id = uuid.uuid4()
        gift_id = uuid.uuid4()

        existing = _make_gift(user_id=user_id, gift_id=gift_id, status=GiftStatusEnum.idee)
        mock_repo.get_by_id.return_value = existing
        mock_repo.update.return_value = existing

        update_data = GiftUpdate(status=GiftStatusEnum.achete)

        result = service.update(user_id, gift_id, update_data)

        assert result.status == GiftStatusEnum.achete

    def test_update_gift_recipients(self):
        mock_repo = Mock()
        mock_recipient_repo = Mock()
        service = GiftService(mock_repo, mock_recipient_repo)

        user_id = uuid.uuid4()
        gift_id = uuid.uuid4()
        rid = uuid.uuid4()

        existing = _make_gift(user_id=user_id, gift_id=gift_id)
        recipient = _make_recipient(user_id, rid)
        mock_repo.get_by_id.return_value = existing
        mock_recipient_repo.get_by_id.return_value = recipient
        mock_repo.update.return_value = existing

        update_data = GiftUpdate(recipient_ids=[rid])

        result = service.update(user_id, gift_id, update_data)

        assert result.recipient_ids == [rid]
        mock_recipient_repo.get_by_id.assert_called_once_with(user_id, rid)

    def test_update_gift_not_found_raises_404(self):
        mock_repo = Mock()
        mock_recipient_repo = Mock()
        service = GiftService(mock_repo, mock_recipient_repo)

        user_id = uuid.uuid4()
        gift_id = uuid.uuid4()

        mock_repo.get_by_id.return_value = None

        update_data = GiftUpdate(name="New Name")

        with pytest.raises(HTTPException) as exc_info:
            service.update(user_id, gift_id, update_data)

        assert exc_info.value.status_code == 404
        mock_repo.update.assert_not_called()

    def test_update_gift_invalid_recipient_raises_404(self):
        mock_repo = Mock()
        mock_recipient_repo = Mock()
        service = GiftService(mock_repo, mock_recipient_repo)

        user_id = uuid.uuid4()
        gift_id = uuid.uuid4()
        rid = uuid.uuid4()

        existing = _make_gift(user_id=user_id, gift_id=gift_id)
        mock_repo.get_by_id.return_value = existing
        mock_recipient_repo.get_by_id.return_value = None

        update_data = GiftUpdate(recipient_ids=[rid])

        with pytest.raises(HTTPException) as exc_info:
            service.update(user_id, gift_id, update_data)

        assert exc_info.value.status_code == 404
        mock_repo.update.assert_not_called()

    def test_update_gift_no_fields_provided(self):
        mock_repo = Mock()
        mock_recipient_repo = Mock()
        service = GiftService(mock_repo, mock_recipient_repo)

        user_id = uuid.uuid4()
        gift_id = uuid.uuid4()

        existing = _make_gift(user_id=user_id, gift_id=gift_id, name="Name", price=Decimal("10.00"))
        mock_repo.get_by_id.return_value = existing
        mock_repo.update.return_value = existing

        update_data = GiftUpdate()

        result = service.update(user_id, gift_id, update_data)

        assert result.name == "Name"
        mock_repo.update.assert_called_once()


class TestGiftServiceDelete:

    def test_delete_gift_success(self):
        mock_repo = Mock()
        mock_recipient_repo = Mock()
        service = GiftService(mock_repo, mock_recipient_repo)

        user_id = uuid.uuid4()
        gift_id = uuid.uuid4()

        mock_repo.delete.return_value = True

        service.delete(user_id, gift_id)

        mock_repo.delete.assert_called_once_with(user_id, gift_id)

    def test_delete_gift_not_found_raises_404(self):
        mock_repo = Mock()
        mock_recipient_repo = Mock()
        service = GiftService(mock_repo, mock_recipient_repo)

        user_id = uuid.uuid4()
        gift_id = uuid.uuid4()

        mock_repo.delete.return_value = False

        with pytest.raises(HTTPException) as exc_info:
            service.delete(user_id, gift_id)

        assert exc_info.value.status_code == 404
        assert "not found" in exc_info.value.detail.lower()

    def test_delete_gift_wrong_user_raises_404(self):
        mock_repo = Mock()
        mock_recipient_repo = Mock()
        service = GiftService(mock_repo, mock_recipient_repo)

        user_id = uuid.uuid4()
        gift_id = uuid.uuid4()

        mock_repo.delete.return_value = False

        with pytest.raises(HTTPException) as exc_info:
            service.delete(user_id, gift_id)

        assert exc_info.value.status_code == 404
