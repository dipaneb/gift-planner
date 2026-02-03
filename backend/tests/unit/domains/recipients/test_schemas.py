import pytest
import uuid
from pydantic import ValidationError

from src.domains.recipients.schemas import RecipientCreate, RecipientUpdate, RecipientResponse


class TestRecipientCreate:
    
    def test_valid_recipient_with_notes(self):
        data = {
            "name": "Test Recipient",
            "notes": "Some notes"
        }
        
        recipient = RecipientCreate(**data)
        
        assert recipient.name == "Test Recipient"
        assert recipient.notes == "Some notes"
    
    def test_valid_recipient_without_notes(self):
        data = {
            "name": "Test Recipient"
        }
        
        recipient = RecipientCreate(**data)
        
        assert recipient.name == "Test Recipient"
        assert recipient.notes is None
    
    def test_valid_recipient_with_none_notes(self):
        data = {
            "name": "Test Recipient",
            "notes": None
        }
        
        recipient = RecipientCreate(**data)
        
        assert recipient.notes is None
    
    def test_missing_name_raises_validation_error(self):
        data = {
            "notes": "Some notes"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            RecipientCreate(**data)
        
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("name",) for error in errors)
    
    def test_name_normalization_strips_whitespace(self):
        data = {
            "name": "  Test Recipient  "
        }
        
        recipient = RecipientCreate(**data)
        
        assert recipient.name == "Test Recipient"
    
    def test_notes_normalization_strips_whitespace(self):
        data = {
            "name": "Test",
            "notes": "  Some notes  "
        }
        
        recipient = RecipientCreate(**data)
        
        assert recipient.notes == "Some notes"
    
    def test_empty_name_after_strip_raises_validation_error(self):
        data = {
            "name": "   "  # Only whitespace
        }
        
        with pytest.raises(ValidationError) as exc_info:
            RecipientCreate(**data)
        
        errors = exc_info.value.errors()
        assert any("empty" in str(error["msg"]).lower() for error in errors)
    
    def test_empty_notes_after_strip_becomes_none(self):
        data = {
            "name": "Test",
            "notes": "   "  # Only whitespace
        }
        
        recipient = RecipientCreate(**data)
        
        assert recipient.notes is None
    
    def test_name_too_long_raises_validation_error(self):
        data = {
            "name": "A" * 256  # Exceeds 255 char limit
        }
        
        with pytest.raises(ValidationError) as exc_info:
            RecipientCreate(**data)
        
        errors = exc_info.value.errors()
        assert any(error["type"] == "string_too_long" for error in errors)
    
    def test_notes_too_long_raises_validation_error(self):
        data = {
            "name": "Test",
            "notes": "A" * 6001  # Exceeds 6000 char limit
        }
        
        with pytest.raises(ValidationError) as exc_info:
            RecipientCreate(**data)
        
        errors = exc_info.value.errors()
        assert any(error["type"] == "string_too_long" for error in errors)
    
    def test_name_max_length_is_valid(self):
        data = {
            "name": "A" * 255  # Exactly at limit
        }
        
        recipient = RecipientCreate(**data)
        
        assert len(recipient.name) == 255
    
    def test_notes_max_length_is_valid(self):
        data = {
            "name": "Test",
            "notes": "A" * 6000  # Exactly at limit
        }
        
        recipient = RecipientCreate(**data)
        
        assert len(recipient.notes) == 6000


class TestRecipientUpdate:
    
    def test_update_name_only(self):
        data = {
            "name": "Updated Name"
        }
        
        update = RecipientUpdate(**data)
        
        assert update.name == "Updated Name"
        assert update.notes is None
    
    def test_update_notes_only(self):
        data = {
            "notes": "Updated notes"
        }
        
        update = RecipientUpdate(**data)
        
        assert update.name is None
        assert update.notes == "Updated notes"
    
    def test_update_both_fields(self):
        data = {
            "name": "Updated Name",
            "notes": "Updated notes"
        }
        
        update = RecipientUpdate(**data)
        
        assert update.name == "Updated Name"
        assert update.notes == "Updated notes"
    
    def test_update_with_no_fields(self):
        data = {}
        
        update = RecipientUpdate(**data)
        
        assert update.name is None
        assert update.notes is None
    
    def test_update_name_normalization(self):
        data = {
            "name": "  Updated Name  "
        }
        
        update = RecipientUpdate(**data)
        
        assert update.name == "Updated Name"
    
    def test_update_notes_normalization(self):
        data = {
            "notes": "  Updated notes  "
        }
        
        update = RecipientUpdate(**data)
        
        assert update.notes == "Updated notes"
    
    def test_update_empty_name_after_strip_raises_validation_error(self):
        data = {
            "name": "   "
        }
        
        with pytest.raises(ValidationError) as exc_info:
            RecipientUpdate(**data)
        
        errors = exc_info.value.errors()
        assert any("empty" in str(error["msg"]).lower() for error in errors)
    
    def test_update_empty_notes_after_strip_becomes_none(self):
        data = {
            "notes": "   "
        }
        
        update = RecipientUpdate(**data)
        
        assert update.notes is None
    
    def test_update_name_too_long_raises_validation_error(self):
        data = {
            "name": "A" * 256
        }
        
        with pytest.raises(ValidationError) as exc_info:
            RecipientUpdate(**data)
        
        errors = exc_info.value.errors()
        assert any(error["type"] == "string_too_long" for error in errors)
    
    def test_update_notes_too_long_raises_validation_error(self):
        data = {
            "notes": "A" * 6001
        }
        
        with pytest.raises(ValidationError) as exc_info:
            RecipientUpdate(**data)
        
        errors = exc_info.value.errors()
        assert any(error["type"] == "string_too_long" for error in errors)
    
    def test_update_clear_notes_with_none(self):
        data = {
            "notes": None
        }
        
        update = RecipientUpdate(**data)
        
        assert update.notes is None
    
    def test_model_dump_exclude_unset(self):
        """Test that only provided fields are included in model_dump(exclude_unset=True)"""
        data = {
            "name": "Updated Name"
            # notes not provided
        }
        
        update = RecipientUpdate(**data)
        dump = update.model_dump(exclude_unset=True)
        
        assert "name" in dump
        assert "notes" not in dump


class TestRecipientResponse:
    
    def test_valid_response(self):
        data = {
            "id": str(uuid.uuid4()),
            "user_id": str(uuid.uuid4()),
            "name": "Test Recipient",
            "notes": "Test notes"
        }
        
        response = RecipientResponse(**data)
        
        assert isinstance(response.id, uuid.UUID)
        assert isinstance(response.user_id, uuid.UUID)
        assert response.name == "Test Recipient"
        assert response.notes == "Test notes"
    
    def test_response_without_notes(self):
        data = {
            "id": str(uuid.uuid4()),
            "user_id": str(uuid.uuid4()),
            "name": "Test Recipient",
            "notes": None
        }
        
        response = RecipientResponse(**data)
        
        assert response.notes is None
    
    def test_response_from_orm_model(self):
        """Test from_attributes config works with ORM models"""
        from src.domains.recipients.models import Recipient
        
        recipient_id = uuid.uuid4()
        user_id = uuid.uuid4()
        
        # Create mock ORM object
        class MockRecipient:
            id = recipient_id
            user_id = user_id
            name = "ORM Recipient"
            notes = "ORM Notes"
        
        response = RecipientResponse.model_validate(MockRecipient())
        
        assert response.id == recipient_id
        assert response.user_id == user_id
        assert response.name == "ORM Recipient"
        assert response.notes == "ORM Notes"
    
    def test_missing_required_fields_raises_validation_error(self):
        data = {
            "id": str(uuid.uuid4()),
            # Missing user_id and name
        }
        
        with pytest.raises(ValidationError) as exc_info:
            RecipientResponse(**data)
        
        errors = exc_info.value.errors()
        field_names = [error["loc"][0] for error in errors]
        assert "user_id" in field_names
        assert "name" in field_names
    
    def test_invalid_uuid_raises_validation_error(self):
        data = {
            "id": "not-a-uuid",
            "user_id": str(uuid.uuid4()),
            "name": "Test",
            "notes": None
        }
        
        with pytest.raises(ValidationError) as exc_info:
            RecipientResponse(**data)
        
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("id",) for error in errors)
    
    def test_response_serialization(self):
        """Test that response can be serialized to dict"""
        recipient_id = uuid.uuid4()
        user_id = uuid.uuid4()
        
        data = {
            "id": str(recipient_id),
            "user_id": str(user_id),
            "name": "Test Recipient",
            "notes": "Test notes"
        }
        
        response = RecipientResponse(**data)
        serialized = response.model_dump()
        
        assert serialized["id"] == recipient_id
        assert serialized["user_id"] == user_id
        assert serialized["name"] == "Test Recipient"
        assert serialized["notes"] == "Test notes"
