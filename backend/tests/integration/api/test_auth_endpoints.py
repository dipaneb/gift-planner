import pytest
from fastapi.testclient import TestClient


class TestRegisterEndpoint:
    
    def test_register_success(self, client, valid_user_data):
        response = client.post("/auth/register", json=valid_user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data
        assert "user" in data
        assert "id" in data["user"]
        assert data["user"]["id"] is not None
    
    def test_register_success_without_name(self, client, valid_user_data_no_name):
        response = client.post("/auth/register", json=valid_user_data_no_name)
        
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert "id" in data["user"]
    
    def test_register_duplicate_email_returns_409(self, client, valid_user_data):
        response1 = client.post("/auth/register", json=valid_user_data)
        assert response1.status_code == 201
        
        response2 = client.post("/auth/register", json=valid_user_data)
        assert response2.status_code == 409
        assert "already in use" in response2.json()["detail"].lower()
    
    def test_register_duplicate_email_with_existing_user(self, client, sample_user):
        user_data = {
            "email": sample_user.email,
            "password": "NewPassword123!",
            "confirmed_password": "NewPassword123!",
            "name": "New User"
        }
        
        response = client.post("/auth/register", json=user_data)
        assert response.status_code == 409
    
    def test_register_invalid_email_returns_422(self, client):
        user_data = {
            "email": "invalid-email",
            "password": "SecurePass123!",
            "confirmed_password": "SecurePass123!",
            "name": "Test User"
        }
        
        response = client.post("/auth/register", json=user_data)
        assert response.status_code == 422
    
    def test_register_weak_password_returns_422(self, client):
        user_data = {
            "email": "test@example.com",
            "password": "weak",
            "confirmed_password": "weak",
            "name": "Test User"
        }
        
        response = client.post("/auth/register", json=user_data)
        assert response.status_code == 422
    
    def test_register_password_mismatch_returns_422(self, client):
        user_data = {
            "email": "test@example.com",
            "password": "SecurePass123!",
            "confirmed_password": "DifferentPass123!",
            "name": "Test User"
        }
        
        response = client.post("/auth/register", json=user_data)
        assert response.status_code == 422
    
    def test_register_missing_required_fields_returns_422(self, client):
        incomplete_data = {
            "email": "test@example.com"
        }
        
        response = client.post("/auth/register", json=incomplete_data)
        assert response.status_code == 422
    
    def test_register_password_without_uppercase_returns_422(self, client):
        user_data = {
            "email": "test@example.com",
            "password": "lowercase123!",
            "confirmed_password": "lowercase123!",
            "name": "Test User"
        }
        
        response = client.post("/auth/register", json=user_data)
        assert response.status_code == 422
        assert "uppercase" in response.text.lower()
    
    def test_register_password_without_digit_returns_422(self, client):
        user_data = {
            "email": "test@example.com",
            "password": "NoDigitsHere!",
            "confirmed_password": "NoDigitsHere!",
            "name": "Test User"
        }
        
        response = client.post("/auth/register", json=user_data)
        assert response.status_code == 422
        assert "digit" in response.text.lower()
    
    def test_register_password_without_special_char_returns_422(self, client):
        user_data = {
            "email": "test@example.com",
            "password": "NoSpecial123",
            "confirmed_password": "NoSpecial123",
            "name": "Test User"
        }
        
        response = client.post("/auth/register", json=user_data)
        assert response.status_code == 422
        assert "special" in response.text.lower()
    
    def test_register_multiple_users_success(self, client, db_session):
        from src.domains.users.repository import UserRepository
        
        user1_data = {
            "email": "user1@example.com",
            "password": "SecurePass123!",
            "confirmed_password": "SecurePass123!",
            "name": "User One"
        }
        user2_data = {
            "email": "user2@example.com",
            "password": "SecurePass456!",
            "confirmed_password": "SecurePass456!",
            "name": "User Two"
        }
        
        response1 = client.post("/auth/register", json=user1_data)
        response2 = client.post("/auth/register", json=user2_data)
        
        assert response1.status_code == 201
        assert response2.status_code == 201
        assert response1.json()["user"]["id"] != response2.json()["user"]["id"]
        
        repo = UserRepository(db_session)
        user1 = repo.get_by_email("user1@example.com")
        user2 = repo.get_by_email("user2@example.com")
        assert user1 is not None
        assert user2 is not None
        assert user1.name == "User One"
        assert user2.name == "User Two"
    
    def test_register_normalizes_whitespace_in_name(self, client, db_session):
        from src.domains.users.repository import UserRepository
        
        user_data = {
            "email": "whitespace@example.com",
            "password": "SecurePass123!",
            "confirmed_password": "SecurePass123!",
            "name": "  Test User  "
        }
        
        response = client.post("/auth/register", json=user_data)
        assert response.status_code == 201
        
        repo = UserRepository(db_session)
        created_user = repo.get_by_email("whitespace@example.com")
        assert created_user is not None
        assert created_user.name == "Test User"
    
    def test_register_empty_name_becomes_none(self, client, db_session):
        from src.domains.users.repository import UserRepository
        
        user_data = {
            "email": "emptyname@example.com",
            "password": "SecurePass123!",
            "confirmed_password": "SecurePass123!",
            "name": "   "
        }
        
        response = client.post("/auth/register", json=user_data)
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert "id" in data["user"]
        
        repo = UserRepository(db_session)
        created_user = repo.get_by_email("emptyname@example.com")
        assert created_user is not None
        assert created_user.name is None
    
    def test_register_long_password_accepted(self, client, db_session):
        from src.domains.users.repository import UserRepository
        from src.domains.auth.password_handler import verify_password
        
        long_password = "VeryLongSecurePassword123!" * 5
        user_data = {
            "email": "longpass@example.com",
            "password": long_password,
            "confirmed_password": long_password,
            "name": "Test User"
        }
        
        response = client.post("/auth/register", json=user_data)
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        
        repo = UserRepository(db_session)
        created_user = repo.get_by_email("longpass@example.com")
        assert created_user is not None
        assert verify_password(long_password, created_user.password_hash)
