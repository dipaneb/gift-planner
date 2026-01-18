import pytest
from pydantic import ValidationError

from src.domains.auth.schemas import UserCreate


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
        special_chars = ["!", "@", "#", "$", "%", "^", "&", "*"]
        for char in special_chars:
            data = {
                "email": "test@example.com",
                "password": f"SecurePass123{char}",
                "confirmed_password": f"SecurePass123{char}",
            }
            user = UserCreate(**data)
            assert user.password == data["password"]
