import pytest
from fastapi import status

from src.domains.users.models import User
from src.domains.auth.password_handler import get_password_hash
from src.domains.users.repository import UserRepository


class TestLoginEndpoint:
    
    @pytest.fixture
    def registered_user(self, db_session):
        user = User(
            email="john@example.com",
            password_hash=get_password_hash("SecurePass123!"),
            name="John Doe",
            is_verified=True
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user
    
    def test_login_success(self, client, registered_user):
        response = client.post(
            "/auth/login",
            data={
                "username": "john@example.com",
                "password": "SecurePass123!"
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert "access_token" in data
        assert "token_type" in data
        assert "expires_in" in data
        assert data["token_type"] == "bearer"
        assert isinstance(data["access_token"], str)
        assert len(data["access_token"]) > 0
        assert isinstance(data["expires_in"], int)
        assert data["expires_in"] > 0
    
    def test_login_sets_refresh_token_cookie(self, client, registered_user):
        response = client.post(
            "/auth/login",
            data={
                "username": "john@example.com",
                "password": "SecurePass123!"
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert "refresh_token" in response.cookies
        
        refresh_cookie = response.cookies.get("refresh_token")
        assert refresh_cookie is not None
        assert len(refresh_cookie) > 0
    
    def test_login_refresh_token_cookie_attributes(self, client, registered_user):
        response = client.post(
            "/auth/login",
            data={
                "username": "john@example.com",
                "password": "SecurePass123!"
            }
        )
        
        cookies = response.headers.get("set-cookie", "")
        
        assert "httponly" in cookies.lower()
        assert "samesite=strict" in cookies.lower()
        assert "path=/auth" in cookies.lower()
    
    def test_login_invalid_email(self, client):
        response = client.post(
            "/auth/login",
            data={
                "username": "nonexistent@example.com",
                "password": "SomePassword123!"
            }
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert "detail" in data
        assert "Invalid email or password" in data["detail"]
    
    def test_login_invalid_password(self, client, registered_user):
        response = client.post(
            "/auth/login",
            data={
                "username": "john@example.com",
                "password": "WrongPassword123!"
            }
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert "Invalid email or password" in data["detail"]
    
    def test_login_case_sensitive_password(self, client, registered_user):
        response = client.post(
            "/auth/login",
            data={
                "username": "john@example.com",
                "password": "securepass123!"
            }
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_login_email_case_insensitive(self, client, registered_user):
        response = client.post(
            "/auth/login",
            data={
                "username": "JOHN@EXAMPLE.COM",
                "password": "SecurePass123!"
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
    
    def test_login_missing_username(self, client):
        response = client.post(
            "/auth/login",
            data={
                "password": "SecurePass123!"
            }
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_login_missing_password(self, client):
        response = client.post(
            "/auth/login",
            data={
                "username": "john@example.com"
            }
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_login_empty_username(self, client):
        response = client.post(
            "/auth/login",
            data={
                "username": "",
                "password": "SecurePass123!"
            }
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_login_empty_password(self, client, registered_user):
        response = client.post(
            "/auth/login",
            data={
                "username": "john@example.com",
                "password": ""
            }
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_login_creates_refresh_token_in_database(self, client, db_session, registered_user):
        from src.domains.auth.models import RefreshToken
        from sqlalchemy import select, func
        
        stmt = select(func.count()).select_from(RefreshToken).where(RefreshToken.user_id == registered_user.id)
        initial_count = db_session.execute(stmt).scalar()
        
        response = client.post(
            "/auth/login",
            data={
                "username": "john@example.com",
                "password": "SecurePass123!"
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        final_count = db_session.execute(stmt).scalar()
        assert final_count == initial_count + 1
    
    def test_login_multiple_times_creates_multiple_refresh_tokens(self, client, db_session, registered_user):
        from src.domains.auth.models import RefreshToken
        from sqlalchemy import select
        
        response1 = client.post(
            "/auth/login",
            data={"username": "john@example.com", "password": "SecurePass123!"}
        )
        response2 = client.post(
            "/auth/login",
            data={"username": "john@example.com", "password": "SecurePass123!"}
        )
        
        assert response1.status_code == status.HTTP_200_OK
        assert response2.status_code == status.HTTP_200_OK
        
        stmt = select(RefreshToken).where(RefreshToken.user_id == registered_user.id)
        tokens = db_session.execute(stmt).scalars().all()
        assert len(tokens) >= 2
        
        token1_cookie = response1.cookies.get("refresh_token")
        token2_cookie = response2.cookies.get("refresh_token")
        assert token1_cookie != token2_cookie
    
    def test_login_access_token_contains_user_id(self, client, registered_user):
        import jwt
        from src.config.settings import get_settings
        
        response = client.post(
            "/auth/login",
            data={
                "username": "john@example.com",
                "password": "SecurePass123!"
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        access_token = response.json()["access_token"]
        
        settings = get_settings()
        decoded = jwt.decode(access_token, settings.SECRET_KEY, algorithms=["HS256"])
        
        assert decoded["sub"] == str(registered_user.id)
    
    def test_login_different_users_get_different_tokens(self, client, db_session):
        user1 = User(
            email="user1@example.com",
            password_hash=get_password_hash("Password123!"),
            name="User One",
            is_verified=True
        )
        user2 = User(
            email="user2@example.com",
            password_hash=get_password_hash("Password123!"),
            name="User Two",
            is_verified=True
        )
        db_session.add(user1)
        db_session.add(user2)
        db_session.commit()
        
        response1 = client.post(
            "/auth/login",
            data={"username": "user1@example.com", "password": "Password123!"}
        )
        response2 = client.post(
            "/auth/login",
            data={"username": "user2@example.com", "password": "Password123!"}
        )
        
        assert response1.status_code == status.HTTP_200_OK
        assert response2.status_code == status.HTTP_200_OK
        
        token1 = response1.json()["access_token"]
        token2 = response2.json()["access_token"]
        
        assert token1 != token2
    
    def test_login_with_whitespace_in_username(self, client, registered_user):
        response = client.post(
            "/auth/login",
            data={
                "username": "  john@example.com  ",
                "password": "SecurePass123!"
            }
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_login_sql_injection_attempt(self, client, registered_user):
        response = client.post(
            "/auth/login",
            data={
                "username": "john@example.com' OR '1'='1",
                "password": "SecurePass123!"
            }
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_login_unverified_email_returns_403(self, client, db_session):
        """Test that users with unverified emails cannot log in. 403 is safe here because correct password is required to reach this check."""
        unverified_user = User(
            email="unverified@example.com",
            password_hash=get_password_hash("SecurePass123!"),
            name="Unverified User",
            is_verified=False
        )
        db_session.add(unverified_user)
        db_session.commit()
        
        response = client.post(
            "/auth/login",
            data={
                "username": "unverified@example.com",
                "password": "SecurePass123!"
            }
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        data = response.json()
        assert "verify" in data["detail"].lower()
