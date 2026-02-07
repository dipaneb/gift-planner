import pytest
import uuid
from unittest.mock import Mock, MagicMock
from fastapi import HTTPException

from src.domains.recipients.service import RecipientService
from src.domains.recipients.models import Recipient
from src.domains.recipients.schemas import RecipientUpdate


class TestRecipientServiceCreate:
    
    def test_create_recipient_success(self):
        mock_repo = Mock()
        service = RecipientService(mock_repo)
        
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
        mock_repo.create.return_value = expected_recipient
        
        result = service.create(user_id, name, notes)
        
        assert result == expected_recipient
        mock_repo.create.assert_called_once()
        created_recipient = mock_repo.create.call_args[0][0]
        assert created_recipient.user_id == user_id
        assert created_recipient.name == name
        assert created_recipient.notes == notes
    
    def test_create_recipient_without_notes(self):
        mock_repo = Mock()
        service = RecipientService(mock_repo)
        
        user_id = uuid.uuid4()
        name = "Test Recipient"
        
        expected_recipient = Recipient(
            id=uuid.uuid4(),
            user_id=user_id,
            name=name,
            notes=None
        )
        mock_repo.create.return_value = expected_recipient
        
        result = service.create(user_id, name, None)
        
        assert result.notes is None
        mock_repo.create.assert_called_once()


class TestRecipientServiceGet:
    
    def test_get_recipients_success(self):
        mock_repo = Mock()
        service = RecipientService(mock_repo)
        
        user_id = uuid.uuid4()
        pagination = {"sort": "asc", "page": 1, "limit": 10}
        
        recipients = [
            Recipient(id=uuid.uuid4(), user_id=user_id, name="Recipient 1", notes=None),
            Recipient(id=uuid.uuid4(), user_id=user_id, name="Recipient 2", notes=None),
        ]
        mock_repo.get.return_value = (recipients, 2)
        
        result = service.get(pagination, user_id)
        
        assert len(result.items) == 2
        assert result.meta.total == 2
        assert result.meta.page == 1
        mock_repo.get.assert_called_once_with(pagination, user_id)
    
    def test_get_recipients_empty_list(self):
        mock_repo = Mock()
        service = RecipientService(mock_repo)
        
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
        service = RecipientService(mock_repo)
        
        user_id = uuid.uuid4()
        recipient_id = uuid.uuid4()
        
        expected_recipient = Recipient(
            id=recipient_id,
            user_id=user_id,
            name="Test Recipient",
            notes="Test notes"
        )
        mock_repo.get_by_id.return_value = expected_recipient
        
        result = service.get_by_id(user_id, recipient_id)
        
        assert result == expected_recipient
        mock_repo.get_by_id.assert_called_once_with(user_id, recipient_id)
    
    def test_get_by_id_not_found_raises_404(self):
        mock_repo = Mock()
        service = RecipientService(mock_repo)
        
        user_id = uuid.uuid4()
        recipient_id = uuid.uuid4()
        
        mock_repo.get_by_id.return_value = None
        
        with pytest.raises(HTTPException) as exc_info:
            service.get_by_id(user_id, recipient_id)
        
        assert exc_info.value.status_code == 404
        assert "not found" in exc_info.value.detail.lower()
    
    def test_get_by_id_wrong_user_raises_404(self):
        mock_repo = Mock()
        service = RecipientService(mock_repo)
        
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
        service = RecipientService(mock_repo)
        
        user_id = uuid.uuid4()
        recipient_id = uuid.uuid4()
        
        existing_recipient = Recipient(
            id=recipient_id,
            user_id=user_id,
            name="Original Name",
            notes="Original Notes"
        )
        mock_repo.get_by_id.return_value = existing_recipient
        mock_repo.update.return_value = existing_recipient
        
        update_data = RecipientUpdate(name="Updated Name")
        
        result = service.update(user_id, recipient_id, update_data)
        
        assert result.name == "Updated Name"
        assert result.notes == "Original Notes"  # Unchanged
        mock_repo.update.assert_called_once_with(existing_recipient)
    
    def test_update_recipient_notes_only(self):
        mock_repo = Mock()
        service = RecipientService(mock_repo)
        
        user_id = uuid.uuid4()
        recipient_id = uuid.uuid4()
        
        existing_recipient = Recipient(
            id=recipient_id,
            user_id=user_id,
            name="Name",
            notes="Original Notes"
        )
        mock_repo.get_by_id.return_value = existing_recipient
        mock_repo.update.return_value = existing_recipient
        
        update_data = RecipientUpdate(notes="Updated Notes")
        
        result = service.update(user_id, recipient_id, update_data)
        
        assert result.name == "Name"  # Unchanged
        assert result.notes == "Updated Notes"
    
    def test_update_recipient_both_fields(self):
        mock_repo = Mock()
        service = RecipientService(mock_repo)
        
        user_id = uuid.uuid4()
        recipient_id = uuid.uuid4()
        
        existing_recipient = Recipient(
            id=recipient_id,
            user_id=user_id,
            name="Original",
            notes="Original"
        )
        mock_repo.get_by_id.return_value = existing_recipient
        mock_repo.update.return_value = existing_recipient
        
        update_data = RecipientUpdate(name="New Name", notes="New Notes")
        
        result = service.update(user_id, recipient_id, update_data)
        
        assert result.name == "New Name"
        assert result.notes == "New Notes"
    
    def test_update_recipient_not_found_raises_404(self):
        mock_repo = Mock()
        service = RecipientService(mock_repo)
        
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
        service = RecipientService(mock_repo)
        
        user_id = uuid.uuid4()
        recipient_id = uuid.uuid4()
        
        existing_recipient = Recipient(
            id=recipient_id,
            user_id=user_id,
            name="Name",
            notes="Notes"
        )
        mock_repo.get_by_id.return_value = existing_recipient
        mock_repo.update.return_value = existing_recipient
        
        # Empty update
        update_data = RecipientUpdate()
        
        result = service.update(user_id, recipient_id, update_data)
        
        # Nothing should change
        assert result.name == "Name"
        assert result.notes == "Notes"
        mock_repo.update.assert_called_once()


class TestRecipientServiceDelete:
    
    def test_delete_recipient_success(self):
        mock_repo = Mock()
        service = RecipientService(mock_repo)
        
        user_id = uuid.uuid4()
        recipient_id = uuid.uuid4()
        
        mock_repo.delete.return_value = True
        
        # Should not raise
        service.delete(user_id, recipient_id)
        
        mock_repo.delete.assert_called_once_with(user_id, recipient_id)
    
    def test_delete_recipient_not_found_raises_404(self):
        mock_repo = Mock()
        service = RecipientService(mock_repo)
        
        user_id = uuid.uuid4()
        recipient_id = uuid.uuid4()
        
        mock_repo.delete.return_value = False
        
        with pytest.raises(HTTPException) as exc_info:
            service.delete(user_id, recipient_id)
        
        assert exc_info.value.status_code == 404
        assert "not found" in exc_info.value.detail.lower()
    
    def test_delete_recipient_wrong_user_raises_404(self):
        mock_repo = Mock()
        service = RecipientService(mock_repo)
        
        user_id = uuid.uuid4()
        recipient_id = uuid.uuid4()
        
        # Repo returns False when user doesn't match
        mock_repo.delete.return_value = False
        
        with pytest.raises(HTTPException) as exc_info:
            service.delete(user_id, recipient_id)
        
        assert exc_info.value.status_code == 404
