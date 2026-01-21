import pytest
import uuid
from unittest.mock import Mock

import jwt
from fastapi import HTTPException

from src.domains.auth.dependencies import get_current_user_id, get_current_user, _unauthorized
from src.domains.users.repository import UserRepository
from src.domains.users.models import User
from src.config.settings import get_settings

settings = get_settings()


class TestUnauthorizedHelper:
    
    def test_unauthorized_returns_new_instance_each_time(self):
        exc1 = _unauthorized()
        exc2 = _unauthorized()
        
        assert exc1 is not exc2
        assert exc1.status_code == 401
        assert exc1.detail == "Not authenticated"
        assert exc1.headers == {"WWW-Authenticate": "Bearer"}


class TestGetCurrentUserId:
    
    def test_get_current_user_id_valid_token(self):
        user_id = uuid.uuid4()
        token = jwt.encode({"sub": str(user_id)}, settings.SECRET_KEY, algorithm="HS256")
        
        result = get_current_user_id(token)
        
        assert result == user_id
    
    def test_get_current_user_id_missing_sub(self):
        token = jwt.encode({"other": "data"}, settings.SECRET_KEY, algorithm="HS256")
        
        with pytest.raises(HTTPException) as exc_info:
            get_current_user_id(token)
        
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Not authenticated"
    
    def test_get_current_user_id_invalid_token(self):
        invalid_token = "not.a.valid.token"
        
        with pytest.raises(HTTPException) as exc_info:
            get_current_user_id(invalid_token)
        
        assert exc_info.value.status_code == 401
    
    def test_get_current_user_id_tampered_token(self):
        user_id = uuid.uuid4()
        token = jwt.encode({"sub": str(user_id)}, "wrong_secret", algorithm="HS256")
        
        with pytest.raises(HTTPException) as exc_info:
            get_current_user_id(token)
        
        assert exc_info.value.status_code == 401
    
    def test_get_current_user_id_expired_token(self):
        import time
        user_id = uuid.uuid4()
        token = jwt.encode(
            {"sub": str(user_id), "exp": int(time.time()) - 3600},
            settings.SECRET_KEY,
            algorithm="HS256"
        )
        
        with pytest.raises(HTTPException) as exc_info:
            get_current_user_id(token)
        
        assert exc_info.value.status_code == 401
    
    def test_get_current_user_id_sub_not_valid_uuid(self):
        token = jwt.encode({"sub": "not-a-uuid"}, settings.SECRET_KEY, algorithm="HS256")
        
        with pytest.raises(HTTPException) as exc_info:
            get_current_user_id(token)
        
        assert exc_info.value.status_code == 401


class TestGetCurrentUser:
    
    def test_get_current_user_existing_user(self):
        user_id = uuid.uuid4()
        user = User(
            id=user_id,
            email="test@example.com",
            password_hash="hash",
            name="Test User"
        )
        
        mock_repo = Mock(spec=UserRepository)
        mock_repo.get_by_id.return_value = user
        
        result = get_current_user(user_id, mock_repo)
        
        assert result == user
        mock_repo.get_by_id.assert_called_once_with(user_id)
    
    def test_get_current_user_non_existing_user(self):
        user_id = uuid.uuid4()
        
        mock_repo = Mock(spec=UserRepository)
        mock_repo.get_by_id.return_value = None
        
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(user_id, mock_repo)
        
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Not authenticated"
    
    def test_get_current_user_calls_repository(self):
        user_id = uuid.uuid4()
        user = User(
            id=user_id,
            email="test@example.com",
            password_hash="hash",
            name="Test User"
        )
        
        mock_repo = Mock(spec=UserRepository)
        mock_repo.get_by_id.return_value = user
        
        get_current_user(user_id, mock_repo)
        
        mock_repo.get_by_id.assert_called_once_with(user_id)
