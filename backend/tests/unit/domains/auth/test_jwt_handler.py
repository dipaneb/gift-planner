import pytest
import jwt
from datetime import datetime, timezone, timedelta

from src.domains.auth.jwt_handler import create_access_token
from src.config.settings import get_settings

settings = get_settings()


class TestCreateAccessToken:
    
    def test_create_access_token_structure(self):
        subject = "user-123"
        expires_minutes = 15
        
        token = create_access_token(subject=subject, expires_minutes=expires_minutes)
        
        assert isinstance(token, str)
        assert len(token) > 0
        
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        assert decoded["sub"] == subject
        assert "iat" in decoded
        assert "exp" in decoded
    
    def test_create_access_token_expiration(self):
        subject = "user-456"
        expires_minutes = 30
        
        before = datetime.now(timezone.utc)
        token = create_access_token(subject=subject, expires_minutes=expires_minutes)
        after = datetime.now(timezone.utc)
        
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        
        expected_exp_before = int((before + timedelta(minutes=expires_minutes)).timestamp())
        expected_exp_after = int((after + timedelta(minutes=expires_minutes)).timestamp())
        
        assert decoded["exp"] >= expected_exp_before
        assert decoded["exp"] <= expected_exp_after
        assert decoded["iat"] >= int(before.timestamp())
        assert decoded["iat"] <= int(after.timestamp())
    
    def test_create_access_token_with_different_subjects(self):
        token1 = create_access_token(subject="user-1", expires_minutes=15)
        token2 = create_access_token(subject="user-2", expires_minutes=15)
        
        decoded1 = jwt.decode(token1, settings.SECRET_KEY, algorithms=["HS256"])
        decoded2 = jwt.decode(token2, settings.SECRET_KEY, algorithms=["HS256"])
        
        assert decoded1["sub"] != decoded2["sub"]
        assert decoded1["sub"] == "user-1"
        assert decoded2["sub"] == "user-2"
    
    def test_create_access_token_with_custom_expiration(self):
        token_short = create_access_token(subject="user-123", expires_minutes=5)
        token_long = create_access_token(subject="user-123", expires_minutes=60)
        
        decoded_short = jwt.decode(token_short, settings.SECRET_KEY, algorithms=["HS256"])
        decoded_long = jwt.decode(token_long, settings.SECRET_KEY, algorithms=["HS256"])
        
        assert decoded_long["exp"] > decoded_short["exp"]
    
    def test_create_access_token_can_be_verified(self):
        subject = "user-789"
        token = create_access_token(subject=subject, expires_minutes=15)
        
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        assert decoded["sub"] == subject
    
    def test_create_access_token_invalid_secret_raises_error(self):
        token = create_access_token(subject="user-123", expires_minutes=15)
        
        with pytest.raises(jwt.InvalidSignatureError):
            jwt.decode(token, "wrong-secret", algorithms=["HS256"])
