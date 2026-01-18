import pytest
from unittest.mock import Mock, MagicMock
from fastapi import HTTPException
from src.domains.auth.service import UserService
from src.domains.auth.schemas import UserCreate
from src.domains.users.models import User


class TestUserServiceRegisterUser:
    
    def test_register_user_success(self, db_session, valid_user_data):
        from src.domains.auth.repository import UserRepository
        
        repo = UserRepository(db_session)
        service = UserService(repo)
        user_create = UserCreate(**valid_user_data)
        
        created_user = service.register_user(user_create)
        
        assert created_user.id is not None
        assert created_user.email == valid_user_data["email"]
        assert created_user.name == valid_user_data["name"]
        assert created_user.password_hash != valid_user_data["password"]
        assert len(created_user.password_hash) > 0
    
    def test_register_user_without_name(self, db_session, valid_user_data_no_name):
        from src.domains.auth.repository import UserRepository
        
        repo = UserRepository(db_session)
        service = UserService(repo)
        user_create = UserCreate(**valid_user_data_no_name)
        
        created_user = service.register_user(user_create)
        
        assert created_user.id is not None
        assert created_user.email == valid_user_data_no_name["email"]
        assert created_user.name is None
    
    def test_register_user_hashes_password(self, db_session, valid_user_data):
        from src.domains.auth.repository import UserRepository
        from src.domains.auth.password_handler import verify_password
        
        repo = UserRepository(db_session)
        service = UserService(repo)
        user_create = UserCreate(**valid_user_data)
        
        created_user = service.register_user(user_create)
        
        assert verify_password(valid_user_data["password"], created_user.password_hash)
    
    def test_register_user_duplicate_email_raises_409(self, db_session, sample_user, valid_user_data):
        from src.domains.auth.repository import UserRepository
        
        repo = UserRepository(db_session)
        service = UserService(repo)
        
        duplicate_data = valid_user_data.copy()
        duplicate_data["email"] = sample_user.email
        user_create = UserCreate(**duplicate_data)
        
        with pytest.raises(HTTPException) as exc_info:
            service.register_user(user_create)
        
        assert exc_info.value.status_code == 409
        assert "already in use" in exc_info.value.detail.lower()
    
    def test_register_user_duplicate_detection_case_insensitive(self, db_session, sample_user, valid_user_data):
        from src.domains.auth.repository import UserRepository
        
        repo = UserRepository(db_session)
        service = UserService(repo)
        
        duplicate_data = valid_user_data.copy()
        duplicate_data["email"] = sample_user.email.upper()
        user_create = UserCreate(**duplicate_data)
        
        with pytest.raises(HTTPException) as exc_info:
            service.register_user(user_create)
        
        assert exc_info.value.status_code == 409
        assert "already in use" in exc_info.value.detail.lower()
    
    def test_register_user_normalizes_email_to_lowercase(self, db_session):
        from src.domains.auth.repository import UserRepository
        
        repo = UserRepository(db_session)
        service = UserService(repo)
        
        user_create = UserCreate(
            email="NewUser@EXAMPLE.COM",
            password="SecurePass123!",
            confirmed_password="SecurePass123!",
            name="Test User"
        )
        
        created_user = service.register_user(user_create)
        assert created_user.email == "newuser@example.com"


class TestUserServiceWithMockedRepository:
    
    def test_register_user_calls_repository_methods(self, valid_user_data):
        mock_repo = Mock()
        mock_repo.get_by_email.return_value = None
        
        expected_user = User(
            email=valid_user_data["email"],
            password_hash="hashed",
            name=valid_user_data["name"]
        )
        mock_repo.create.return_value = expected_user
        
        service = UserService(mock_repo)
        user_create = UserCreate(**valid_user_data)
        
        result = service.register_user(user_create)
        
        mock_repo.get_by_email.assert_called_once_with(valid_user_data["email"])
        mock_repo.create.assert_called_once()
        assert result == expected_user
    
    def test_register_user_does_not_call_create_on_duplicate(self, valid_user_data):
        mock_repo = Mock()
        existing_user = User(
            email=valid_user_data["email"],
            password_hash="existing_hash",
            name="Existing"
        )
        mock_repo.get_by_email.return_value = existing_user
        
        service = UserService(mock_repo)
        user_create = UserCreate(**valid_user_data)
        
        with pytest.raises(HTTPException):
            service.register_user(user_create)
        
        mock_repo.get_by_email.assert_called_once()
        mock_repo.create.assert_not_called()
