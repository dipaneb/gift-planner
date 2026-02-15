import pytest
from fastapi import status

from src.domains.users.models import User
from src.domains.auth.password_handler import get_password_hash


class TestUsersMeEndpoint:
    
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
    
    @pytest.fixture
    def access_token(self, client, registered_user):
        response = client.post(
            "/auth/login",
            data={
                "username": "john@example.com",
                "password": "SecurePass123!"
            }
        )
        return response.json()["access_token"]
    
    def test_get_me_success(self, client, registered_user, access_token):
        response = client.get(
            "/users/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["id"] == str(registered_user.id)
        assert data["email"] == registered_user.email
        assert data["name"] == registered_user.name
    
    def test_get_me_without_token(self, client):
        response = client.get("/users/me")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_me_with_invalid_token(self, client):
        response = client.get(
            "/users/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == "Not authenticated"
    
    def test_get_me_with_expired_token(self, client, registered_user):
        import jwt
        from datetime import datetime, timezone, timedelta
        from src.config.settings import get_settings
        
        settings = get_settings()
        expired_token = jwt.encode(
            {
                "sub": str(registered_user.id),
                "exp": datetime.now(timezone.utc) - timedelta(hours=1)
            },
            settings.SECRET_KEY,
            algorithm="HS256"
        )
        
        response = client.get(
            "/users/me",
            headers={"Authorization": f"Bearer {expired_token}"}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_me_with_token_for_deleted_user(self, client, db_session):
        import jwt
        import uuid
        from src.config.settings import get_settings
        
        settings = get_settings()
        non_existent_id = uuid.uuid4()
        token = jwt.encode(
            {"sub": str(non_existent_id)},
            settings.SECRET_KEY,
            algorithm="HS256"
        )
        
        response = client.get(
            "/users/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_me_without_name(self, client, db_session):
        user = User(
            email="noname@example.com",
            password_hash=get_password_hash("SecurePass123!"),
            name=None,
            is_verified=True
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        login_response = client.post(
            "/auth/login",
            data={
                "username": "noname@example.com",
                "password": "SecurePass123!"
            }
        )
        access_token = login_response.json()["access_token"]
        
        response = client.get(
            "/users/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] is None
        assert data["email"] == "noname@example.com"
    
    def test_get_me_token_with_missing_sub(self, client):
        import jwt
        from src.config.settings import get_settings
        
        settings = get_settings()
        token = jwt.encode(
            {"other_field": "value"},
            settings.SECRET_KEY,
            algorithm="HS256"
        )
        
        response = client.get(
            "/users/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
