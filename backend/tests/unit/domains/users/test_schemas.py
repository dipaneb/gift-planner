import pytest
import uuid
from pydantic import ValidationError

from src.domains.users.schemas import UserRead


class TestUserReadSchema:
    
    def test_user_read_valid(self):
        user_id = uuid.uuid4()
        user_data = UserRead(
            id=user_id,
            email="test@example.com",
            name="Test User"
        )
        
        assert user_data.id == user_id
        assert user_data.email == "test@example.com"
        assert user_data.name == "Test User"
    
    def test_user_read_without_name(self):
        user_id = uuid.uuid4()
        user_data = UserRead(
            id=user_id,
            email="test@example.com",
            name=None
        )
        
        assert user_data.id == user_id
        assert user_data.email == "test@example.com"
        assert user_data.name is None
    
    def test_user_read_invalid_email(self):
        user_id = uuid.uuid4()
        
        with pytest.raises(ValidationError) as exc_info:
            UserRead(
                id=user_id,
                email="invalid-email",
                name="Test"
            )
        
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("email",) for e in errors)
    
    def test_user_read_missing_id(self):
        with pytest.raises(ValidationError) as exc_info:
            UserRead(
                email="test@example.com",
                name="Test"
            )
        
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("id",) for e in errors)
    
    def test_user_read_missing_email(self):
        with pytest.raises(ValidationError) as exc_info:
            UserRead(
                id=uuid.uuid4(),
                name="Test"
            )
        
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("email",) for e in errors)
    
    def test_user_read_serialization(self):
        user_id = uuid.uuid4()
        user_data = UserRead(
            id=user_id,
            email="test@example.com",
            name="Test User"
        )
        
        serialized = user_data.model_dump()
        
        assert serialized["id"] == user_id
        assert serialized["email"] == "test@example.com"
        assert serialized["name"] == "Test User"
