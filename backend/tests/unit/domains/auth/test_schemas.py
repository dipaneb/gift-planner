import pytest
import uuid
from pydantic import ValidationError

from src.domains.auth.schemas import UserCreate, LoginData, UserUpdatePartial, UserResponse


class TestUserCreateSchema:
    
    def test_valid_user_create(self, valid_user_data):
        user = UserCreate(**valid_user_data)
        assert user.email == valid_user_data["email"]
        assert user.password == valid_user_data["password"]
        assert user.name == valid_user_data["name"]
    
    def test_valid_user_create_without_name(self, valid_user_data_no_name):
        user = UserCreate(**valid_user_data_no_name)
        assert user.email == valid_user_data_no_name["email"]
        assert user.name is None
    
    def test_name_normalization_strips_whitespace(self):
        data = {
            "email": "test@example.com",
            "password": "SecurePass123!",
            "confirmed_password": "SecurePass123!",
            "name": "  Test User  "
        }
        user = UserCreate(**data)
        assert user.name == "Test User"
    
    def test_name_normalization_empty_string_becomes_none(self):
        data = {
            "email": "test@example.com",
            "password": "SecurePass123!",
            "confirmed_password": "SecurePass123!",
            "name": "   "
        }
        user = UserCreate(**data)
        assert user.name is None


class TestEmailValidation:
    
    def test_invalid_email_format(self):
        data = {
            "email": "invalid-email",
            "password": "SecurePass123!",
            "confirmed_password": "SecurePass123!",
        }
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**data)
        assert "email" in str(exc_info.value)
    
    def test_valid_email_formats(self):
        valid_emails = [
            "test@example.com",
            "user.name@example.co.uk",
            "user+tag@example.com",
            "123@example.com"
        ]
        for email in valid_emails:
            data = {
                "email": email,
                "password": "SecurePass123!",
                "confirmed_password": "SecurePass123!",
            }
            user = UserCreate(**data)
            assert user.email == email


class TestPasswordValidation:
    
    def test_password_too_short(self):
        data = {
            "email": "test@example.com",
            "password": "Short1!",
            "confirmed_password": "Short1!",
        }
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**data)
        assert "password" in str(exc_info.value).lower()
    
    def test_password_missing_uppercase(self):
        data = {
            "email": "test@example.com",
            "password": "lowercase123!",
            "confirmed_password": "lowercase123!",
        }
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**data)
        assert "uppercase" in str(exc_info.value).lower()
    
    def test_password_missing_lowercase(self):
        data = {
            "email": "test@example.com",
            "password": "UPPERCASE123!",
            "confirmed_password": "UPPERCASE123!",
        }
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**data)
        assert "lowercase" in str(exc_info.value).lower()
    
    def test_password_missing_digit(self):
        data = {
            "email": "test@example.com",
            "password": "NoDigitsHere!",
            "confirmed_password": "NoDigitsHere!",
        }
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**data)
        assert "digit" in str(exc_info.value).lower()
    
    def test_password_missing_special_character(self):
        data = {
            "email": "test@example.com",
            "password": "NoSpecial123",
            "confirmed_password": "NoSpecial123",
        }
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**data)
        assert "special" in str(exc_info.value).lower()
    
    def test_password_mismatch(self):
        data = {
            "email": "test@example.com",
            "password": "SecurePass123!",
            "confirmed_password": "DifferentPass123!",
        }
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**data)
        assert "match" in str(exc_info.value).lower()
    
    def test_password_valid_with_various_special_chars(self):
        # Test all basic ASCII special characters (excluding whitespace only)
        special_chars = [
            "!", '"', "#", "$", "%", "&", "'", "(", ")", "*", "+", ",", "-", ".", "/",
            ":", ";", "<", "=", ">", "?", "@", "[", "\\", "]", "^", "_", "`", "{", "|", "}", "~"
        ]
        for char in special_chars:
            data = {
                "email": "test@example.com",
                "password": f"SecurePass123{char}",
                "confirmed_password": f"SecurePass123{char}",
            }
            user = UserCreate(**data)
            assert user.password == data["password"]
    
    def test_password_invalid_with_space_only(self):
        # Space should NOT count as a special character
        data = {
            "email": "test@example.com",
            "password": "SecurePass123 ",
            "confirmed_password": "SecurePass123 ",
        }
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**data)
        assert "special" in str(exc_info.value).lower()


class TestLoginDataSchema:
    
    @pytest.fixture
    def sample_user_response(self):
        return UserResponse(id=uuid.uuid4(), email="test@example.com", name="Test")

    def test_login_data_valid(self, sample_user_response):
        data = LoginData(
            access_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            expires_in=900,
            user=sample_user_response
        )
        
        assert data.access_token == "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        assert data.token_type == "bearer"
        assert data.expires_in == 900
        assert data.user == sample_user_response
    
    def test_login_data_default_token_type(self, sample_user_response):
        data = LoginData(
            access_token="some_token",
            expires_in=600,
            user=sample_user_response
        )
        
        assert data.token_type == "bearer"
    
    def test_login_data_custom_token_type(self, sample_user_response):
        data = LoginData(
            access_token="some_token",
            token_type="Bearer",
            expires_in=600,
            user=sample_user_response
        )
        
        assert data.token_type == "Bearer"
    
    def test_login_data_missing_access_token(self, sample_user_response):
        with pytest.raises(ValidationError) as exc_info:
            LoginData(expires_in=900, user=sample_user_response)
        
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("access_token",) for e in errors)
    
    def test_login_data_missing_expires_in(self, sample_user_response):
        with pytest.raises(ValidationError) as exc_info:
            LoginData(access_token="token", user=sample_user_response)
        
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("expires_in",) for e in errors)
    
    def test_login_data_expires_in_as_string_coerced(self, sample_user_response):
        data = LoginData(access_token="token", expires_in="900", user=sample_user_response)
        assert data.expires_in == 900
    
    def test_login_data_expires_in_invalid_string(self, sample_user_response):
        with pytest.raises(ValidationError):
            LoginData(access_token="token", expires_in="not_a_number", user=sample_user_response)
    
    def test_login_data_serialization(self, sample_user_response):
        data = LoginData(
            access_token="test_token_123",
            expires_in=1800,
            user=sample_user_response
        )
        
        serialized = data.model_dump()
        
        assert serialized["access_token"] == "test_token_123"
        assert serialized["token_type"] == "bearer"
        assert serialized["expires_in"] == 1800
        assert "user" in serialized
    
    def test_login_data_with_zero_expires_in(self, sample_user_response):
        data = LoginData(
            access_token="token",
            expires_in=0,
            user=sample_user_response
        )
        
        assert data.expires_in == 0
    
    def test_login_data_with_large_expires_in(self, sample_user_response):
        data = LoginData(
            access_token="token",
            expires_in=86400,
            user=sample_user_response
        )
        
        assert data.expires_in == 86400
