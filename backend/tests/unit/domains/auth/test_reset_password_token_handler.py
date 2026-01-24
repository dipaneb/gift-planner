import pytest
import hashlib

from src.domains.auth.reset_password_token_handler import (
    hash_token,
    verify_reset_password_token,
    get_reset_password_token_fingerprint
)


class TestHashToken:
    
    def test_hash_token_returns_string(self):
        raw_token = "test_token_123"
        result = hash_token(raw_token)
        
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_hash_token_different_tokens_produce_different_hashes(self):
        token1 = "token_abc"
        token2 = "token_xyz"
        
        hash1 = hash_token(token1)
        hash2 = hash_token(token2)
        
        assert hash1 != hash2
    
    def test_hash_token_same_input_produces_different_hashes(self):
        token = "same_token"
        
        hash1 = hash_token(token)
        hash2 = hash_token(token)
        
        assert hash1 != hash2


class TestVerifyResetPasswordToken:
    
    def test_verify_correct_token(self):
        raw_token = "correct_token_123"
        token_hash = hash_token(raw_token)
        
        result = verify_reset_password_token(raw_token, token_hash)
        
        assert result is True
    
    def test_verify_incorrect_token(self):
        raw_token = "correct_token"
        wrong_token = "wrong_token"
        token_hash = hash_token(raw_token)
        
        result = verify_reset_password_token(wrong_token, token_hash)
        
        assert result is False
    
    def test_verify_with_empty_string(self):
        token_hash = hash_token("valid_token")
        
        result = verify_reset_password_token("", token_hash)
        
        assert result is False
    
    def test_verify_token_with_special_characters(self):
        raw_token = "token!@#$%^&*()_+-=[]{}|;:',.<>?/~`"
        token_hash = hash_token(raw_token)
        
        result = verify_reset_password_token(raw_token, token_hash)
        
        assert result is True


class TestGetResetPasswordTokenFingerprint:
    
    def test_fingerprint_returns_string(self):
        raw_token = "test_token"
        result = get_reset_password_token_fingerprint(raw_token)
        
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_fingerprint_is_deterministic(self):
        raw_token = "same_token"
        
        fp1 = get_reset_password_token_fingerprint(raw_token)
        fp2 = get_reset_password_token_fingerprint(raw_token)
        
        assert fp1 == fp2
    
    def test_fingerprint_different_tokens_produce_different_fingerprints(self):
        token1 = "token_one"
        token2 = "token_two"
        
        fp1 = get_reset_password_token_fingerprint(token1)
        fp2 = get_reset_password_token_fingerprint(token2)
        
        assert fp1 != fp2
    
    def test_fingerprint_is_sha256_hex(self):
        raw_token = "test_token"
        result = get_reset_password_token_fingerprint(raw_token)
        
        expected = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
        assert result == expected
    
    def test_fingerprint_length_is_64_characters(self):
        raw_token = "any_token"
        result = get_reset_password_token_fingerprint(raw_token)
        
        assert len(result) == 64
    
    def test_fingerprint_with_empty_string(self):
        result = get_reset_password_token_fingerprint("")
        
        expected = hashlib.sha256("".encode("utf-8")).hexdigest()
        assert result == expected
    
    def test_fingerprint_with_unicode_characters(self):
        raw_token = "token_🔒_émojî"
        result = get_reset_password_token_fingerprint(raw_token)
        
        expected = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
        assert result == expected
