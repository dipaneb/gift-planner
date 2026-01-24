import pytest
import uuid
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock, patch

from fastapi import HTTPException

from src.domains.auth.service import AuthService
from src.domains.auth.schemas import UserCreate
from src.domains.users.models import User
from src.domains.users.repository import UserRepository
from src.domains.auth.repository import RefreshTokenRepository, ResetPasswordRepository
from src.domains.auth.models import RefreshToken
from src.domains.auth.password_handler import get_password_hash


class TestAuthServiceRegisterUser:
    
    def test_register_user_success(self, db_session, valid_user_data):
        user_repo = UserRepository(db_session)
        refresh_repo = RefreshTokenRepository(db_session)
        reset_password_repo = ResetPasswordRepository(db_session)
        service = AuthService(user_repo, refresh_repo, reset_password_repo)
        user_create = UserCreate(**valid_user_data)
        
        created_user = service.register_user(user_create)
        
        assert created_user.id is not None
        assert created_user.email == valid_user_data["email"]
        assert created_user.name == valid_user_data["name"]
        assert created_user.password_hash != valid_user_data["password"]
        assert len(created_user.password_hash) > 0
    
    def test_register_user_without_name(self, db_session, valid_user_data_no_name):
        user_repo = UserRepository(db_session)
        refresh_repo = RefreshTokenRepository(db_session)
        reset_password_repo = ResetPasswordRepository(db_session)
        service = AuthService(user_repo, refresh_repo, reset_password_repo)
        user_create = UserCreate(**valid_user_data_no_name)
        
        created_user = service.register_user(user_create)
        
        assert created_user.id is not None
        assert created_user.email == valid_user_data_no_name["email"]
        assert created_user.name is None
    
    def test_register_user_hashes_password(self, db_session, valid_user_data):
        from src.domains.auth.password_handler import verify_password
        
        user_repo = UserRepository(db_session)
        refresh_repo = RefreshTokenRepository(db_session)
        reset_password_repo = ResetPasswordRepository(db_session)
        service = AuthService(user_repo, refresh_repo, reset_password_repo)
        user_create = UserCreate(**valid_user_data)
        
        created_user = service.register_user(user_create)
        
        assert verify_password(valid_user_data["password"], created_user.password_hash)
    
    def test_register_user_duplicate_email_raises_409(self, db_session, sample_user, valid_user_data):
        user_repo = UserRepository(db_session)
        refresh_repo = RefreshTokenRepository(db_session)
        reset_password_repo = ResetPasswordRepository(db_session)
        service = AuthService(user_repo, refresh_repo, reset_password_repo)
        
        duplicate_data = valid_user_data.copy()
        duplicate_data["email"] = sample_user.email
        user_create = UserCreate(**duplicate_data)
        
        with pytest.raises(HTTPException) as exc_info:
            service.register_user(user_create)
        
        assert exc_info.value.status_code == 409
        assert "already in use" in exc_info.value.detail.lower()
    
    def test_register_user_duplicate_detection_case_insensitive(self, db_session, sample_user, valid_user_data):
        user_repo = UserRepository(db_session)
        refresh_repo = RefreshTokenRepository(db_session)
        reset_password_repo = ResetPasswordRepository(db_session)
        service = AuthService(user_repo, refresh_repo, reset_password_repo)
        
        duplicate_data = valid_user_data.copy()
        duplicate_data["email"] = sample_user.email.upper()
        user_create = UserCreate(**duplicate_data)
        
        with pytest.raises(HTTPException) as exc_info:
            service.register_user(user_create)
        
        assert exc_info.value.status_code == 409
        assert "already in use" in exc_info.value.detail.lower()
    
    def test_register_user_normalizes_email_to_lowercase(self, db_session):
        user_repo = UserRepository(db_session)
        refresh_repo = RefreshTokenRepository(db_session)
        reset_password_repo = ResetPasswordRepository(db_session)
        service = AuthService(user_repo, refresh_repo, reset_password_repo)
        
        user_create = UserCreate(
            email="NewUser@EXAMPLE.COM",
            password="SecurePass123!",
            confirmed_password="SecurePass123!",
            name="Test User"
        )
        
        created_user = service.register_user(user_create)
        assert created_user.email == "newuser@example.com"
    
    def test_register_user_calls_repository_methods(self, valid_user_data):
        mock_user_repo = Mock()
        mock_user_repo.get_by_email.return_value = None
        
        expected_user = User(
            email=valid_user_data["email"],
            password_hash="hashed",
            name=valid_user_data["name"]
        )
        mock_user_repo.create.return_value = expected_user
        
        mock_refresh_repo = Mock()
        mock_reset_password_repo = Mock()
        service = AuthService(mock_user_repo, mock_refresh_repo, mock_reset_password_repo)
        user_create = UserCreate(**valid_user_data)
        
        result = service.register_user(user_create)
        
        mock_user_repo.get_by_email.assert_called_once_with(valid_user_data["email"])
        mock_user_repo.create.assert_called_once()
        assert result == expected_user
    
    def test_register_user_calls_create_on_user_repo(self, valid_user_data):
        mock_user_repo = Mock()
        expected_user = User(
            id=uuid.uuid4(),
            email=valid_user_data["email"],
            password_hash="hashed",
            name=valid_user_data["name"]
        )
        mock_user_repo.get_by_email.return_value = None
        mock_user_repo.create.return_value = expected_user
        
        mock_refresh_repo = Mock()
        mock_reset_password_repo = Mock()
        service = AuthService(mock_user_repo, mock_refresh_repo, mock_reset_password_repo)
        user_create = UserCreate(**valid_user_data)
        
        result = service.register_user(user_create)
        
        mock_user_repo.get_by_email.assert_called_once_with(valid_user_data["email"])
        mock_user_repo.create.assert_called_once()
        assert result == expected_user
    
    def test_register_user_does_not_call_create_on_duplicate(self, valid_user_data):
        mock_user_repo = Mock()
        existing_user = User(
            email=valid_user_data["email"],
            password_hash="existing_hash",
            name="Existing"
        )
        mock_user_repo.get_by_email.return_value = existing_user
        
        mock_refresh_repo = Mock()
        mock_reset_password_repo = Mock()
        service = AuthService(mock_user_repo, mock_refresh_repo, mock_reset_password_repo)
        user_create = UserCreate(**valid_user_data)
        
        with pytest.raises(HTTPException):
            service.register_user(user_create)
        
        mock_user_repo.get_by_email.assert_called_once()
        mock_user_repo.create.assert_not_called()


class TestAuthServiceLogin:
    
    @pytest.fixture
    def mock_user_repo(self):
        return Mock(spec=UserRepository)
    
    @pytest.fixture
    def mock_refresh_token_repo(self):
        return Mock(spec=RefreshTokenRepository)
    
    @pytest.fixture
    def mock_reset_password_repo(self):
        return Mock(spec=ResetPasswordRepository)
    
    @pytest.fixture
    def auth_service(self, mock_user_repo, mock_refresh_token_repo, mock_reset_password_repo):
        return AuthService(mock_user_repo, mock_refresh_token_repo, mock_reset_password_repo)
    
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


class TestAuthServiceRotate:
    
    @pytest.fixture
    def mock_user_repo(self):
        return Mock(spec=UserRepository)
    
    @pytest.fixture
    def mock_refresh_token_repo(self):
        return Mock(spec=RefreshTokenRepository)
    
    @pytest.fixture
    def mock_reset_password_repo(self):
        return Mock(spec=ResetPasswordRepository)
    
    @pytest.fixture
    def auth_service(self, mock_user_repo, mock_refresh_token_repo, mock_reset_password_repo):
        return AuthService(mock_user_repo, mock_refresh_token_repo, mock_reset_password_repo)
    
    def test_rotate_success(self, auth_service, mock_refresh_token_repo):
        user_id = uuid.uuid4()
        old_raw_token = "old_token_abc123"
        
        old_token = RefreshToken(
            id=uuid.uuid4(),
            user_id=user_id,
            token_fingerprint="old_fingerprint",
            token_hash="old_hash",
            expires_at=datetime.now(timezone.utc) + timedelta(days=30),
            revoked_at=None
        )
        
        new_token = RefreshToken(
            id=uuid.uuid4(),
            user_id=user_id,
            token_fingerprint="new_fingerprint",
            token_hash="new_hash",
            expires_at=datetime.now(timezone.utc) + timedelta(days=30)
        )
        
        mock_refresh_token_repo.get_by_fingerprint.side_effect = [old_token, new_token]
        
        with patch('src.domains.auth.service.verify_refresh_token', return_value=True):
            returned_user_id, new_raw_token = auth_service.rotate(old_raw_token)
        
        assert returned_user_id == user_id
        assert isinstance(new_raw_token, str)
        assert len(new_raw_token) == 32
        mock_refresh_token_repo.revoke.assert_called_once()
    
    def test_rotate_invalid_token_not_in_db(self, auth_service, mock_refresh_token_repo):
        old_raw_token = "nonexistent_token"
        
        mock_refresh_token_repo.get_by_fingerprint.return_value = None
        
        with pytest.raises(ValueError) as exc_info:
            auth_service.rotate(old_raw_token)
        
        assert str(exc_info.value) == "invalid_refresh"
        mock_refresh_token_repo.revoke.assert_not_called()
    
    def test_rotate_already_revoked_token_triggers_reuse_detection(self, auth_service, mock_refresh_token_repo):
        user_id = uuid.uuid4()
        old_raw_token = "revoked_token"
        
        revoked_token = RefreshToken(
            id=uuid.uuid4(),
            user_id=user_id,
            token_fingerprint="fingerprint",
            token_hash="hash",
            expires_at=datetime.now(timezone.utc) + timedelta(days=30),
            revoked_at=datetime.now(timezone.utc) - timedelta(hours=1)
        )
        
        mock_refresh_token_repo.get_by_fingerprint.return_value = revoked_token
        
        with pytest.raises(ValueError) as exc_info:
            auth_service.rotate(old_raw_token)
        
        assert str(exc_info.value) == "refresh_reuse"
        mock_refresh_token_repo.delete_all_tokens_for_user.assert_called_once_with(user_id)
    
    def test_rotate_expired_token_raises_error(self, auth_service, mock_refresh_token_repo):
        user_id = uuid.uuid4()
        old_raw_token = "expired_token"
        
        expired_token = RefreshToken(
            id=uuid.uuid4(),
            user_id=user_id,
            token_fingerprint="fingerprint",
            token_hash="hash",
            expires_at=datetime.now(timezone.utc) - timedelta(days=1),
            revoked_at=None
        )
        
        mock_refresh_token_repo.get_by_fingerprint.return_value = expired_token
        
        with pytest.raises(ValueError) as exc_info:
            auth_service.rotate(old_raw_token)
        
        assert str(exc_info.value) == "invalid_refresh"
    
    def test_rotate_invalid_token_hash_fails_verification(self, auth_service, mock_refresh_token_repo):
        user_id = uuid.uuid4()
        old_raw_token = "wrong_token"
        
        token = RefreshToken(
            id=uuid.uuid4(),
            user_id=user_id,
            token_fingerprint="fingerprint",
            token_hash="correct_hash",
            expires_at=datetime.now(timezone.utc) + timedelta(days=30),
            revoked_at=None
        )
        
        mock_refresh_token_repo.get_by_fingerprint.return_value = token
        
        with patch('src.domains.auth.service.verify_refresh_token', return_value=False):
            with pytest.raises(ValueError) as exc_info:
                auth_service.rotate(old_raw_token)
        
        assert str(exc_info.value) == "invalid_refresh"
    
    def test_rotate_creates_new_token_and_revokes_old(self, auth_service, mock_refresh_token_repo):
        user_id = uuid.uuid4()
        old_raw_token = "old_token"
        old_token_id = uuid.uuid4()
        
        old_token = RefreshToken(
            id=old_token_id,
            user_id=user_id,
            token_fingerprint="old_fp",
            token_hash="old_hash",
            expires_at=datetime.now(timezone.utc) + timedelta(days=30),
            revoked_at=None
        )
        
        new_token_id = uuid.uuid4()
        new_token = RefreshToken(
            id=new_token_id,
            user_id=user_id,
            token_fingerprint="new_fp",
            token_hash="new_hash",
            expires_at=datetime.now(timezone.utc) + timedelta(days=30)
        )
        
        mock_refresh_token_repo.get_by_fingerprint.side_effect = [old_token, new_token]
        
        with patch('src.domains.auth.service.verify_refresh_token', return_value=True):
            auth_service.rotate(old_raw_token)
        
        mock_refresh_token_repo.create.assert_called_once()
        mock_refresh_token_repo.revoke.assert_called_once_with(old_token_id, replaced_by_id=new_token_id)
    
    def test_rotate_token_expiring_at_exact_moment(self, auth_service, mock_refresh_token_repo):
        user_id = uuid.uuid4()
        old_raw_token = "token"
        
        now = datetime.now(timezone.utc)
        token = RefreshToken(
            id=uuid.uuid4(),
            user_id=user_id,
            token_fingerprint="fp",
            token_hash="hash",
            expires_at=now,
            revoked_at=None
        )
        
        mock_refresh_token_repo.get_by_fingerprint.return_value = token
        
        with pytest.raises(ValueError) as exc_info:
            auth_service.rotate(old_raw_token)
        
        assert str(exc_info.value) == "invalid_refresh"
    
    def test_rotate_new_token_not_found_raises_runtime_error(self, auth_service, mock_refresh_token_repo):
        user_id = uuid.uuid4()
        old_raw_token = "old_token"
        
        old_token = RefreshToken(
            id=uuid.uuid4(),
            user_id=user_id,
            token_fingerprint="old_fp",
            token_hash="old_hash",
            expires_at=datetime.now(timezone.utc) + timedelta(days=30),
            revoked_at=None
        )
        
        mock_refresh_token_repo.get_by_fingerprint.side_effect = [old_token, None]
        
        with patch('src.domains.auth.service.verify_refresh_token', return_value=True):
            with pytest.raises(RuntimeError) as exc_info:
                auth_service.rotate(old_raw_token)
        
        assert str(exc_info.value) == "refresh_rotation_failed"


class TestAuthServiceGlobalLogout:
    
    @pytest.fixture
    def mock_user_repo(self):
        return Mock(spec=UserRepository)
    
    @pytest.fixture
    def mock_refresh_token_repo(self):
        return Mock(spec=RefreshTokenRepository)
    
    @pytest.fixture
    def mock_reset_password_repo(self):
        return Mock(spec=ResetPasswordRepository)
    
    @pytest.fixture
    def auth_service(self, mock_user_repo, mock_refresh_token_repo, mock_reset_password_repo):
        return AuthService(mock_user_repo, mock_refresh_token_repo, mock_reset_password_repo)
    
    def test_global_logout_success(self, auth_service, mock_refresh_token_repo):
        user_id = uuid.uuid4()
        raw_token = "valid_token_abc123"
        
        token = RefreshToken(
            id=uuid.uuid4(),
            user_id=user_id,
            token_fingerprint="fingerprint",
            token_hash="hash",
            expires_at=datetime.now(timezone.utc) + timedelta(days=30),
            revoked_at=None
        )
        
        mock_refresh_token_repo.get_by_fingerprint.return_value = token
        
        with patch('src.domains.auth.service.verify_refresh_token', return_value=True):
            auth_service.global_logout(raw_token)
        
        mock_refresh_token_repo.delete_all_tokens_for_user.assert_called_once_with(user_id)
    
    def test_global_logout_token_not_found_does_not_delete(self, auth_service, mock_refresh_token_repo):
        raw_token = "nonexistent_token"
        
        mock_refresh_token_repo.get_by_fingerprint.return_value = None
        
        auth_service.global_logout(raw_token)
        
        mock_refresh_token_repo.delete_all_tokens_for_user.assert_not_called()
    
    def test_global_logout_invalid_hash_does_not_delete(self, auth_service, mock_refresh_token_repo):
        user_id = uuid.uuid4()
        raw_token = "wrong_token"
        
        token = RefreshToken(
            id=uuid.uuid4(),
            user_id=user_id,
            token_fingerprint="fingerprint",
            token_hash="correct_hash",
            expires_at=datetime.now(timezone.utc) + timedelta(days=30),
            revoked_at=None
        )
        
        mock_refresh_token_repo.get_by_fingerprint.return_value = token
        
        with patch('src.domains.auth.service.verify_refresh_token', return_value=False):
            auth_service.global_logout(raw_token)
        
        mock_refresh_token_repo.delete_all_tokens_for_user.assert_not_called()
    
    def test_global_logout_with_expired_token(self, auth_service, mock_refresh_token_repo):
        user_id = uuid.uuid4()
        raw_token = "expired_token"
        
        token = RefreshToken(
            id=uuid.uuid4(),
            user_id=user_id,
            token_fingerprint="fingerprint",
            token_hash="hash",
            expires_at=datetime.now(timezone.utc) - timedelta(days=1),
            revoked_at=None
        )
        
        mock_refresh_token_repo.get_by_fingerprint.return_value = token
        
        with patch('src.domains.auth.service.verify_refresh_token', return_value=True):
            auth_service.global_logout(raw_token)
        
        mock_refresh_token_repo.delete_all_tokens_for_user.assert_called_once_with(user_id)
    
    def test_global_logout_with_already_revoked_token(self, auth_service, mock_refresh_token_repo):
        user_id = uuid.uuid4()
        raw_token = "revoked_token"
        
        token = RefreshToken(
            id=uuid.uuid4(),
            user_id=user_id,
            token_fingerprint="fingerprint",
            token_hash="hash",
            expires_at=datetime.now(timezone.utc) + timedelta(days=30),
            revoked_at=datetime.now(timezone.utc) - timedelta(hours=1)
        )
        
        mock_refresh_token_repo.get_by_fingerprint.return_value = token
        
        with patch('src.domains.auth.service.verify_refresh_token', return_value=True):
            auth_service.global_logout(raw_token)
        
        mock_refresh_token_repo.delete_all_tokens_for_user.assert_called_once_with(user_id)
