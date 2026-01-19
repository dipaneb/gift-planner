import pytest

from src.domains.auth.refresh_token_handler import hash_token


class TestHashToken:
    
    def test_hash_token_returns_string(self):
        token = "sample-token-123"
        hashed = hash_token(token)
        
        assert isinstance(hashed, str)
        assert len(hashed) > 0
    
    def test_hash_token_is_deterministic_different_inputs(self):
        token1 = "token-abc"
        token2 = "token-xyz"
        
        hash1 = hash_token(token1)
        hash2 = hash_token(token2)
        
        assert hash1 != hash2
    
    def test_hash_token_different_each_time_same_input(self):
        token = "same-token-123"
        
        hash1 = hash_token(token)
        hash2 = hash_token(token)
        
        assert hash1 != hash2
    
    def test_hash_token_with_empty_string(self):
        token = ""
        hashed = hash_token(token)
        
        assert isinstance(hashed, str)
        assert len(hashed) > 0
    
    def test_hash_token_with_long_string(self):
        token = "a" * 1000
        hashed = hash_token(token)
        
        assert isinstance(hashed, str)
        assert len(hashed) > 0
    
    def test_hash_token_with_special_characters(self):
        token = "!@#$%^&*()_+-=[]{}|;:',.<>?/"
        hashed = hash_token(token)
        
        assert isinstance(hashed, str)
        assert len(hashed) > 0
    
    def test_hash_token_with_uuid_format(self):
        token = "550e8400-e29b-41d4-a716-446655440000"
        hashed = hash_token(token)
        
        assert isinstance(hashed, str)
        assert len(hashed) > 0
        assert hashed != token
