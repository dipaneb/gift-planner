import pytest


class TestEmailNormalizationIntegration:
    
    def test_register_email_normalized_to_lowercase(self, client, db_session):
        from src.domains.users.repository import UserRepository
        
        user_data = {
            "email": "MixedCase@EXAMPLE.COM",
            "password": "SecurePass123!",
            "confirmed_password": "SecurePass123!",
            "name": "Test User"
        }
        
        response = client.post("/auth/register", json=user_data)
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert "message" in data
        
        repo = UserRepository(db_session)
        created_user = repo.get_by_email("mixedcase@example.com")
        assert created_user is not None
        assert created_user.email == "mixedcase@example.com"
    
    def test_register_duplicate_email_case_insensitive(self, client):
        user_data = {
            "email": "duplicate@example.com",
            "password": "SecurePass123!",
            "confirmed_password": "SecurePass123!",
            "name": "First User"
        }
        
        response1 = client.post("/auth/register", json=user_data)
        assert response1.status_code == 201
        
        duplicate_data = {
            "email": "DUPLICATE@EXAMPLE.COM",
            "password": "DifferentPass123!",
            "confirmed_password": "DifferentPass123!",
            "name": "Second User"
        }
        
        response2 = client.post("/auth/register", json=duplicate_data)
        assert response2.status_code == 409
        assert "already in use" in response2.json()["detail"].lower()
    
    def test_register_prevents_duplicate_with_mixed_case_variations(self, client):
        variations = [
            "test@example.com",
            "Test@example.com",
            "TEST@EXAMPLE.COM",
            "TeSt@ExAmPlE.cOm"
        ]
        
        first_data = {
            "email": variations[0],
            "password": "SecurePass123!",
            "confirmed_password": "SecurePass123!",
            "name": "First"
        }
        response = client.post("/auth/register", json=first_data)
        assert response.status_code == 201
        
        for email in variations[1:]:
            duplicate_data = {
                "email": email,
                "password": "SecurePass456!",
                "confirmed_password": "SecurePass456!",
                "name": "Duplicate Attempt"
            }
            response = client.post("/auth/register", json=duplicate_data)
            assert response.status_code == 409, f"Failed to reject duplicate email: {email}"
