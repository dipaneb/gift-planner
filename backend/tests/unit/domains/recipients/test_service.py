import pytest
import uuid
from unittest.mock import Mock, MagicMock, patch
from fastapi import HTTPException

from src.domains.recipients.service import RecipientService
from src.domains.recipients.models import Recipient
from src.domains.recipients.schemas import RecipientUpdate


class TestRecipientServiceCreate:
    
    def test_create_recipient_success(self):
        mock_repo = Mock()
        mock_gift_repo = Mock()
        service = RecipientService(mock_repo, mock_gift_repo)
        
        user_id = uuid.uuid4()
        name = "Test Recipient"
        notes = "Test notes"
        
        # Mock repository response
        expected_recipient = Recipient(
            id=uuid.uuid4(),
            user_id=user_id,
            name=name,
            notes=notes
        )
        expected_recipient.gifts = []
        mock_repo.create.return_value = expected_recipient
        
        result = service.create(user_id, name, notes, gift_ids=[])
        
        assert result.name == name
        assert result.notes == notes
        assert result.gift_ids == []
        mock_repo.create.assert_called_once()
        created_recipient = mock_repo.create.call_args[0][0]
        assert created_recipient.user_id == user_id
        assert created_recipient.name == name
        assert created_recipient.notes == notes
    
    def test_create_recipient_without_notes(self):
        mock_repo = Mock()
        mock_gift_repo = Mock()
        service = RecipientService(mock_repo, mock_gift_repo)
        
        user_id = uuid.uuid4()
        name = "Test Recipient"
        
        expected_recipient = Recipient(
            id=uuid.uuid4(),
            user_id=user_id,
            name=name,
            notes=None
        )
        expected_recipient.gifts = []
        mock_repo.create.return_value = expected_recipient
        
        result = service.create(user_id, name, None, gift_ids=[])
        
        assert result.notes is None
        mock_repo.create.assert_called_once()

    @patch('src.domains.recipients.service.Recipient')
    def test_create_recipient_with_gifts(self, MockRecipient):
        mock_repo = Mock()
        mock_gift_repo = Mock()
        service = RecipientService(mock_repo, mock_gift_repo)

        user_id = uuid.uuid4()
        gift_id = uuid.uuid4()
        mock_gift = Mock(id=gift_id)

        # The Recipient() constructor returns our mock instance
        mock_recipient_instance = MockRecipient.return_value
        mock_recipient_instance.gifts = []

        # After repo.create, return a mock with gifts populated
        created_mock = Mock()
        created_mock.id = uuid.uuid4()
        created_mock.user_id = user_id
        created_mock.name = "Mom"
        created_mock.notes = None
        created_mock.gifts = [mock_gift]
        mock_repo.create.return_value = created_mock

        with patch.object(service, '_resolve_gifts', return_value=[mock_gift]) as mock_resolve:
            result = service.create(user_id, "Mom", None, gift_ids=[gift_id])

            assert result.gift_ids == [gift_id]
            mock_resolve.assert_called_once_with(user_id, [gift_id])

    def test_create_recipient_with_invalid_gift_raises_404(self):
        mock_repo = Mock()
        mock_gift_repo = Mock()
        service = RecipientService(mock_repo, mock_gift_repo)

        user_id = uuid.uuid4()
        fake_gift_id = uuid.uuid4()
        mock_gift_repo.get_by_id.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            service.create(user_id, "Mom", None, gift_ids=[fake_gift_id])

        assert exc_info.value.status_code == 404
        mock_repo.create.assert_not_called()


class TestRecipientServiceGet:
    
    def test_get_recipients_success(self):
        mock_repo = Mock()
        mock_gift_repo = Mock()
        service = RecipientService(mock_repo, mock_gift_repo)
        
        user_id = uuid.uuid4()
        pagination = {"sort": "asc", "page": 1, "limit": 10}
        
        r1 = Recipient(id=uuid.uuid4(), user_id=user_id, name="Recipient 1", notes=None)
        r1.gifts = []
        r2 = Recipient(id=uuid.uuid4(), user_id=user_id, name="Recipient 2", notes=None)
        r2.gifts = []
        mock_repo.get.return_value = ([r1, r2], 2)
        
        result = service.get(pagination, user_id)
        
        assert len(result.items) == 2
        assert result.meta.total == 2
        assert result.meta.page == 1
        mock_repo.get.assert_called_once_with(pagination, user_id)
    
    def test_get_recipients_empty_list(self):
        mock_repo = Mock()
        mock_gift_repo = Mock()
        service = RecipientService(mock_repo, mock_gift_repo)
        
        user_id = uuid.uuid4()
        pagination = {"sort": "default", "page": 1, "limit": 10}
        
        mock_repo.get.return_value = ([], 0)
        
        result = service.get(pagination, user_id)
        
        assert result.items == []
        assert result.meta.total == 0
        assert result.meta.totalPages == 0


class TestRecipientServiceGetById:
    
    def test_get_by_id_success(self):
        mock_repo = Mock()
        mock_gift_repo = Mock()
        service = RecipientService(mock_repo, mock_gift_repo)
        
        user_id = uuid.uuid4()
        recipient_id = uuid.uuid4()
        
        expected_recipient = Recipient(
            id=recipient_id,
            user_id=user_id,
            name="Test Recipient",
            notes="Test notes"
        )
        expected_recipient.gifts = []
        mock_repo.get_by_id.return_value = expected_recipient
        
        result = service.get_by_id(user_id, recipient_id)
        
        assert result.id == recipient_id
        assert result.name == "Test Recipient"
        assert result.gift_ids == []
        mock_repo.get_by_id.assert_called_once_with(user_id, recipient_id)
    
    def test_get_by_id_not_found_raises_404(self):
        mock_repo = Mock()
        mock_gift_repo = Mock()
        service = RecipientService(mock_repo, mock_gift_repo)
        
        user_id = uuid.uuid4()
        recipient_id = uuid.uuid4()
        
        mock_repo.get_by_id.return_value = None
        
        with pytest.raises(HTTPException) as exc_info:
            service.get_by_id(user_id, recipient_id)
        
        assert exc_info.value.status_code == 404
        assert "not found" in exc_info.value.detail.lower()
    
    def test_get_by_id_wrong_user_raises_404(self):
        mock_repo = Mock()
        mock_gift_repo = Mock()
        service = RecipientService(mock_repo, mock_gift_repo)
        
        user_id = uuid.uuid4()
        recipient_id = uuid.uuid4()
        
        # Repo returns None when user doesn't match
        mock_repo.get_by_id.return_value = None
        
        with pytest.raises(HTTPException) as exc_info:
            service.get_by_id(user_id, recipient_id)
        
        assert exc_info.value.status_code == 404


class TestRecipientServiceUpdate:
    
    def test_update_recipient_name_only(self):
        mock_repo = Mock()
        mock_gift_repo = Mock()
        service = RecipientService(mock_repo, mock_gift_repo)
        
        user_id = uuid.uuid4()
        recipient_id = uuid.uuid4()
        
        existing_recipient = Recipient(
            id=recipient_id,
            user_id=user_id,
            name="Original Name",
            notes="Original Notes"
        )
        existing_recipient.gifts = []
        mock_repo.get_by_id.return_value = existing_recipient
        mock_repo.update.return_value = existing_recipient
        
        update_data = RecipientUpdate(name="Updated Name")
        
        result = service.update(user_id, recipient_id, update_data)
        
        assert result.name == "Updated Name"
        assert result.notes == "Original Notes"  # Unchanged
        mock_repo.update.assert_called_once_with(existing_recipient)
    
    def test_update_recipient_notes_only(self):
        mock_repo = Mock()
        mock_gift_repo = Mock()
        service = RecipientService(mock_repo, mock_gift_repo)
        
        user_id = uuid.uuid4()
        recipient_id = uuid.uuid4()
        
        existing_recipient = Recipient(
            id=recipient_id,
            user_id=user_id,
            name="Name",
            notes="Original Notes"
        )
        existing_recipient.gifts = []
        mock_repo.get_by_id.return_value = existing_recipient
        mock_repo.update.return_value = existing_recipient
        
        update_data = RecipientUpdate(notes="Updated Notes")
        
        result = service.update(user_id, recipient_id, update_data)
        
        assert result.name == "Name"  # Unchanged
        assert result.notes == "Updated Notes"
    
    def test_update_recipient_both_fields(self):
        mock_repo = Mock()
        mock_gift_repo = Mock()
        service = RecipientService(mock_repo, mock_gift_repo)
        
        user_id = uuid.uuid4()
        recipient_id = uuid.uuid4()
        
        existing_recipient = Recipient(
            id=recipient_id,
            user_id=user_id,
            name="Original",
            notes="Original"
        )
        existing_recipient.gifts = []
        mock_repo.get_by_id.return_value = existing_recipient
        mock_repo.update.return_value = existing_recipient
        
        update_data = RecipientUpdate(name="New Name", notes="New Notes")
        
        result = service.update(user_id, recipient_id, update_data)
        
        assert result.name == "New Name"
        assert result.notes == "New Notes"
    
    def test_update_recipient_not_found_raises_404(self):
        mock_repo = Mock()
        mock_gift_repo = Mock()
        service = RecipientService(mock_repo, mock_gift_repo)
        
        user_id = uuid.uuid4()
        recipient_id = uuid.uuid4()
        
        mock_repo.get_by_id.return_value = None
        
        update_data = RecipientUpdate(name="New Name")
        
        with pytest.raises(HTTPException) as exc_info:
            service.update(user_id, recipient_id, update_data)
        
        assert exc_info.value.status_code == 404
        mock_repo.update.assert_not_called()
    
    def test_update_recipient_no_fields_provided(self):
        mock_repo = Mock()
        mock_gift_repo = Mock()
        service = RecipientService(mock_repo, mock_gift_repo)
        
        user_id = uuid.uuid4()
        recipient_id = uuid.uuid4()
        
        existing_recipient = Recipient(
            id=recipient_id,
            user_id=user_id,
            name="Name",
            notes="Notes"
        )
        existing_recipient.gifts = []
        mock_repo.get_by_id.return_value = existing_recipient
        mock_repo.update.return_value = existing_recipient
        
        # Empty update
        update_data = RecipientUpdate()
        
        result = service.update(user_id, recipient_id, update_data)
        
        # Nothing should change
        assert result.name == "Name"
        assert result.notes == "Notes"
        mock_repo.update.assert_called_once()

    def test_update_recipient_gift_ids(self):
        mock_repo = Mock()
        mock_gift_repo = Mock()
        service = RecipientService(mock_repo, mock_gift_repo)

        user_id = uuid.uuid4()
        recipient_id = uuid.uuid4()
        gift_id = uuid.uuid4()

        mock_gift = Mock(id=gift_id)

        # Use a fully mocked recipient to avoid ORM instrumentation issues
        existing_recipient = Mock()
        existing_recipient.id = recipient_id
        existing_recipient.user_id = user_id
        existing_recipient.name = "Mom"
        existing_recipient.notes = None
        existing_recipient.gifts = []
        mock_repo.get_by_id.return_value = existing_recipient

        with patch.object(service, '_resolve_gifts', return_value=[mock_gift]) as mock_resolve:
            def update_side_effect(r):
                return r
            mock_repo.update.side_effect = update_side_effect

            update_data = RecipientUpdate(gift_ids=[gift_id])
            result = service.update(user_id, recipient_id, update_data)

            assert result.gift_ids == [gift_id]
            mock_resolve.assert_called_once_with(user_id, [gift_id])

    def test_update_recipient_invalid_gift_raises_404(self):
        mock_repo = Mock()
        mock_gift_repo = Mock()
        service = RecipientService(mock_repo, mock_gift_repo)

        user_id = uuid.uuid4()
        recipient_id = uuid.uuid4()

        existing_recipient = Recipient(
            id=recipient_id,
            user_id=user_id,
            name="Mom",
            notes=None,
        )
        existing_recipient.gifts = []
        mock_repo.get_by_id.return_value = existing_recipient
        mock_gift_repo.get_by_id.return_value = None

        update_data = RecipientUpdate(gift_ids=[uuid.uuid4()])

        with pytest.raises(HTTPException) as exc_info:
            service.update(user_id, recipient_id, update_data)

        assert exc_info.value.status_code == 404
        mock_repo.update.assert_not_called()


class TestRecipientServiceDelete:
    
    def test_delete_recipient_success(self):
        mock_repo = Mock()
        mock_gift_repo = Mock()
        service = RecipientService(mock_repo, mock_gift_repo)
        
        user_id = uuid.uuid4()
        recipient_id = uuid.uuid4()
        
        mock_repo.delete.return_value = True
        
        # Should not raise
        service.delete(user_id, recipient_id)
        
        mock_repo.delete.assert_called_once_with(user_id, recipient_id)
    
    def test_delete_recipient_not_found_raises_404(self):
        mock_repo = Mock()
        mock_gift_repo = Mock()
        service = RecipientService(mock_repo, mock_gift_repo)
        
        user_id = uuid.uuid4()
        recipient_id = uuid.uuid4()
        
        mock_repo.delete.return_value = False
        
        with pytest.raises(HTTPException) as exc_info:
            service.delete(user_id, recipient_id)
        
        assert exc_info.value.status_code == 404
        assert "not found" in exc_info.value.detail.lower()
    
    def test_delete_recipient_wrong_user_raises_404(self):
        mock_repo = Mock()
        mock_gift_repo = Mock()
        service = RecipientService(mock_repo, mock_gift_repo)
        
        user_id = uuid.uuid4()
        recipient_id = uuid.uuid4()
        
        # Repo returns False when user doesn't match
        mock_repo.delete.return_value = False
        
        with pytest.raises(HTTPException) as exc_info:
            service.delete(user_id, recipient_id)
        
        assert exc_info.value.status_code == 404
