import pytest
import uuid
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock, patch

from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.domains.auth.service import AuthService
from src.domains.users.repository import UserRepository
from src.domains.auth.repository import RefreshTokenRepository
from src.domains.users.models import User
from src.domains.auth.password_handler import get_password_hash


class TestAuthServiceLogin:
    
    @pytest.fixture
    def mock_user_repo(self):
        return Mock(spec=UserRepository)
    
    @pytest.fixture
    def mock_refresh_token_repo(self):
        return Mock(spec=RefreshTokenRepository)
    
    @pytest.fixture
    def auth_service(self, mock_user_repo, mock_refresh_token_repo):
        return AuthService(mock_user_repo, mock_refresh_token_repo)
    
    @pytest.fixture
    def valid_user(self):
        user = User(
            id=uuid.uuid4(),
            email="test@example.com",
            password_hash=get_password_hash("SecurePass123!"),
            name="Test User"
        )
        return user
    
    def test_login_success(self, auth_service, mock_user_repo, mock_refresh_token_repo, valid_user):
        mock_user_repo.get_by_email.return_value = valid_user
        
        access_token, refresh_token, expires_in = auth_service.login("test@example.com", "SecurePass123!")
        
        assert isinstance(access_token, str)
        assert len(access_token) > 0
        assert isinstance(refresh_token, str)
        assert len(refresh_token) == 32
        assert isinstance(expires_in, int)
        assert expires_in > 0
        
        mock_user_repo.get_by_email.assert_called_once_with("test@example.com")
        mock_refresh_token_repo.create.assert_called_once()
    
    def test_login_invalid_email(self, auth_service, mock_user_repo):
        mock_user_repo.get_by_email.return_value = None
        
        with pytest.raises(HTTPException) as exc_info:
            auth_service.login("nonexistent@example.com", "password")
        
        assert exc_info.value.status_code == 401
        assert "Invalid email or password" in exc_info.value.detail
        assert exc_info.value.headers == {"WWW-Authenticate": "Bearer"}
    
    def test_login_invalid_password(self, auth_service, mock_user_repo, valid_user):
        mock_user_repo.get_by_email.return_value = valid_user
        
        with pytest.raises(HTTPException) as exc_info:
            auth_service.login("test@example.com", "WrongPassword123!")
        
        assert exc_info.value.status_code == 401
        assert "Invalid email or password" in exc_info.value.detail
    
    def test_login_creates_refresh_token(self, auth_service, mock_user_repo, mock_refresh_token_repo, valid_user):
        mock_user_repo.get_by_email.return_value = valid_user
        
        auth_service.login("test@example.com", "SecurePass123!")
        
        mock_refresh_token_repo.create.assert_called_once()
        created_token = mock_refresh_token_repo.create.call_args[0][0]
        
        assert created_token.user_id == valid_user.id
        assert created_token.token_hash is not None
        assert created_token.expires_at > datetime.now(timezone.utc)
    
    def test_login_returns_correct_expires_in(self, auth_service, mock_user_repo, mock_refresh_token_repo, valid_user):
        from src.config.settings import get_settings
        
        mock_user_repo.get_by_email.return_value = valid_user
        settings = get_settings()
        
        _, _, expires_in = auth_service.login("test@example.com", "SecurePass123!")
        
        assert expires_in == settings.ACCESS_TOKEN_LIFESPAN_IN_MINUTES * 60
    
    def test_login_case_sensitive_password(self, auth_service, mock_user_repo, valid_user):
        mock_user_repo.get_by_email.return_value = valid_user
        
        with pytest.raises(HTTPException) as exc_info:
            auth_service.login("test@example.com", "securepass123!")
        
        assert exc_info.value.status_code == 401
    
    def test_login_email_not_case_sensitive(self, auth_service, mock_user_repo, valid_user):
        mock_user_repo.get_by_email.return_value = valid_user
        
        access_token, _, _ = auth_service.login("TEST@EXAMPLE.COM", "SecurePass123!")
        
        assert isinstance(access_token, str)
        mock_user_repo.get_by_email.assert_called_with("test@example.com")
    
    def test_login_multiple_times_creates_different_refresh_tokens(self, auth_service, mock_user_repo, mock_refresh_token_repo, valid_user):
        mock_user_repo.get_by_email.return_value = valid_user
        
        _, refresh1, _ = auth_service.login("test@example.com", "SecurePass123!")
        _, refresh2, _ = auth_service.login("test@example.com", "SecurePass123!")
        
        assert refresh1 != refresh2
        assert mock_refresh_token_repo.create.call_count == 2
    
    def test_login_access_token_contains_user_id(self, auth_service, mock_user_repo, mock_refresh_token_repo, valid_user):
        import jwt
        from src.config.settings import get_settings
        
        mock_user_repo.get_by_email.return_value = valid_user
        settings = get_settings()
        
        access_token, _, _ = auth_service.login("test@example.com", "SecurePass123!")
        
        decoded = jwt.decode(access_token, settings.SECRET_KEY, algorithms=["HS256"])
        assert decoded["sub"] == str(valid_user.id)
    
    def test_login_refresh_token_expiration_set_correctly(self, auth_service, mock_user_repo, mock_refresh_token_repo, valid_user):
        from src.config.settings import get_settings
        
        mock_user_repo.get_by_email.return_value = valid_user
        settings = get_settings()
        
        auth_service.login("test@example.com", "SecurePass123!")
        
        created_token = mock_refresh_token_repo.create.call_args[0][0]
        expected_expiry = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_TTL_DAYS)
        
        assert abs((created_token.expires_at - expected_expiry).total_seconds()) < 2
