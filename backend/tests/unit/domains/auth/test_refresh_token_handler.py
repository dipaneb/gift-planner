import pytest

from src.domains.auth.refresh_token_handler import hash_token, verify_refresh_token, get_refresh_token_fingerprint


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


class TestVerifyRefreshToken:
    
    def test_verify_refresh_token_correct_token(self):
        raw_token = "my_secret_token_123"
        token_hash = hash_token(raw_token)
        
        result = verify_refresh_token(raw_token, token_hash)
        
        assert result is True
    
    def test_verify_refresh_token_incorrect_token(self):
        raw_token = "my_secret_token_123"
        token_hash = hash_token(raw_token)
        
        result = verify_refresh_token("wrong_token", token_hash)
        
        assert result is False
    
    def test_verify_refresh_token_different_tokens(self):
        token1 = "token_one"
        token2 = "token_two"
        hash1 = hash_token(token1)
        
        result = verify_refresh_token(token2, hash1)
        
        assert result is False
    
    def test_verify_refresh_token_case_sensitive(self):
        raw_token = "CaseSensitiveToken"
        token_hash = hash_token(raw_token)
        
        result = verify_refresh_token("casesensitivetoken", token_hash)
        
        assert result is False
    
    def test_verify_refresh_token_with_special_characters(self):
        raw_token = "token!@#$%^&*()_+-="
        token_hash = hash_token(raw_token)
        
        result = verify_refresh_token(raw_token, token_hash)
        
        assert result is True


class TestGetRefreshTokenFingerprint:
    
    def test_get_refresh_token_fingerprint_returns_string(self):
        token = "sample_token_123"
        
        fingerprint = get_refresh_token_fingerprint(token)
        
        assert isinstance(fingerprint, str)
        assert len(fingerprint) > 0
    
    def test_get_refresh_token_fingerprint_is_deterministic(self):
        token = "same_token"
        
        fp1 = get_refresh_token_fingerprint(token)
        fp2 = get_refresh_token_fingerprint(token)
        
        assert fp1 == fp2
    
    def test_get_refresh_token_fingerprint_different_for_different_tokens(self):
        token1 = "token_abc"
        token2 = "token_xyz"
        
        fp1 = get_refresh_token_fingerprint(token1)
        fp2 = get_refresh_token_fingerprint(token2)
        
        assert fp1 != fp2
    
    def test_get_refresh_token_fingerprint_is_sha256(self):
        token = "test_token"
        
        fingerprint = get_refresh_token_fingerprint(token)
        
        assert len(fingerprint) == 64
        assert all(c in '0123456789abcdef' for c in fingerprint)
    
    def test_get_refresh_token_fingerprint_case_sensitive(self):
        token1 = "Token"
        token2 = "token"
        
        fp1 = get_refresh_token_fingerprint(token1)
        fp2 = get_refresh_token_fingerprint(token2)
        
        assert fp1 != fp2
    
    def test_get_refresh_token_fingerprint_with_special_characters(self):
        token = "!@#$%^&*()_+-=[]{}|;:',.<>?/"
        
        fingerprint = get_refresh_token_fingerprint(token)
        
        assert isinstance(fingerprint, str)
        assert len(fingerprint) == 64
    
    def test_get_refresh_token_fingerprint_with_empty_string(self):
        token = ""
        
        fingerprint = get_refresh_token_fingerprint(token)
        
        assert isinstance(fingerprint, str)
        assert len(fingerprint) == 64
