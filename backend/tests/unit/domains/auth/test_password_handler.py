from src.domains.auth.password_handler import get_password_hash, verify_password


class TestPasswordHashing:
    
    def test_hash_password_returns_string(self):
        password = "TestPassword123!"
        hashed = get_password_hash(password)
        assert isinstance(hashed, str)
        assert len(hashed) > 0
    
    def test_hash_password_different_each_time(self):
        password = "TestPassword123!"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        assert hash1 != hash2
    
    def test_hash_password_does_not_contain_plain_password(self):
        password = "TestPassword123!"
        hashed = get_password_hash(password)
        assert password not in hashed


class TestPasswordVerification:
    
    def test_verify_password_correct(self):
        password = "TestPassword123!"
        hashed = get_password_hash(password)
        assert verify_password(password, hashed) is True
    
    def test_verify_password_incorrect(self):
        password = "TestPassword123!"
        wrong_password = "WrongPassword456!"
        hashed = get_password_hash(password)
        assert verify_password(wrong_password, hashed) is False
    
    def test_verify_password_case_sensitive(self):
        password = "TestPassword123!"
        hashed = get_password_hash(password)
        assert verify_password("testpassword123!", hashed) is False
    
    def test_verify_password_empty_string(self):
        password = "TestPassword123!"
        hashed = get_password_hash(password)
        assert verify_password("", hashed) is False
    
    def test_verify_password_with_special_characters(self):
        password = "P@ssw0rd!#$%"
        hashed = get_password_hash(password)
        assert verify_password(password, hashed) is True
