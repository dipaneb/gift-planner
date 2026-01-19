import pytest
from pydantic import ValidationError

from src.domains.auth.schemas import LoginData


class TestLoginDataSchema:
    
    def test_login_data_valid(self):
        data = LoginData(
            access_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            expires_in=900
        )
        
        assert data.access_token == "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        assert data.token_type == "bearer"
        assert data.expires_in == 900
    
    def test_login_data_default_token_type(self):
        data = LoginData(
            access_token="some_token",
            expires_in=600
        )
        
        assert data.token_type == "bearer"
    
    def test_login_data_custom_token_type(self):
        data = LoginData(
            access_token="some_token",
            token_type="Bearer",
            expires_in=600
        )
        
        assert data.token_type == "Bearer"
    
    def test_login_data_missing_access_token(self):
        with pytest.raises(ValidationError) as exc_info:
            LoginData(expires_in=900)
        
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("access_token",) for e in errors)
    
    def test_login_data_missing_expires_in(self):
        with pytest.raises(ValidationError) as exc_info:
            LoginData(access_token="token")
        
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("expires_in",) for e in errors)
    
    def test_login_data_expires_in_as_string_coerced(self):
        data = LoginData(access_token="token", expires_in="900")
        assert data.expires_in == 900
    
    def test_login_data_expires_in_invalid_string(self):
        with pytest.raises(ValidationError):
            LoginData(access_token="token", expires_in="not_a_number")
    
    def test_login_data_serialization(self):
        data = LoginData(
            access_token="test_token_123",
            expires_in=1800
        )
        
        serialized = data.model_dump()
        
        assert serialized["access_token"] == "test_token_123"
        assert serialized["token_type"] == "bearer"
        assert serialized["expires_in"] == 1800
    
    def test_login_data_with_zero_expires_in(self):
        data = LoginData(
            access_token="token",
            expires_in=0
        )
        
        assert data.expires_in == 0
    
    def test_login_data_with_large_expires_in(self):
        data = LoginData(
            access_token="token",
            expires_in=86400
        )
        
        assert data.expires_in == 86400
