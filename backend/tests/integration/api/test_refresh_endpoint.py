import pytest
from fastapi import status
from datetime import datetime, timezone, timedelta
from sqlalchemy import select

from src.domains.users.models import User
from src.domains.auth.models import RefreshToken
from src.domains.auth.password_handler import get_password_hash
from src.domains.auth.refresh_token_handler import get_refresh_token_fingerprint, hash_token


class TestRefreshEndpoint:
    
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
    def logged_in_user_with_refresh_cookie(self, client, registered_user):
        response = client.post(
            "/auth/login",
            data={
                "username": "john@example.com",
                "password": "SecurePass123!"
            }
        )
        return response.cookies.get("refresh_token")
    
    def test_refresh_success(self, client, registered_user, logged_in_user_with_refresh_cookie):
        response = client.post(
            "/auth/refresh",
            cookies={"refresh_token": logged_in_user_with_refresh_cookie}
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
    
    def test_refresh_updates_refresh_token_cookie(self, client, registered_user, logged_in_user_with_refresh_cookie):
        old_refresh_token = logged_in_user_with_refresh_cookie
        
        response = client.post(
            "/auth/refresh",
            cookies={"refresh_token": old_refresh_token}
        )
        
        assert response.status_code == status.HTTP_200_OK
        new_refresh_token = response.cookies.get("refresh_token")
        
        assert new_refresh_token is not None
        assert new_refresh_token != old_refresh_token
    
    def test_refresh_revokes_old_token(self, client, db_session, registered_user, logged_in_user_with_refresh_cookie):
        old_refresh_token = logged_in_user_with_refresh_cookie
        old_fingerprint = get_refresh_token_fingerprint(old_refresh_token)
        
        response = client.post(
            "/auth/refresh",
            cookies={"refresh_token": old_refresh_token}
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        stmt = select(RefreshToken).where(RefreshToken.token_fingerprint == old_fingerprint)
        old_token_in_db = db_session.execute(stmt).scalar_one_or_none()
        
        assert old_token_in_db is not None
        assert old_token_in_db.revoked_at is not None
        assert old_token_in_db.replaced_by_id is not None
    
    def test_refresh_without_cookie_returns_401(self, client):
        response = client.post("/auth/refresh")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Not authenticated" in response.json()["detail"]
    
    def test_refresh_with_invalid_token_returns_401(self, client):
        response = client.post(
            "/auth/refresh",
            cookies={"refresh_token": "invalid_token_xyz"}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Not authenticated" in response.json()["detail"]
    
    def test_refresh_with_expired_token_returns_401(self, client, db_session, registered_user):
        import uuid
        
        raw_token = uuid.uuid4().hex
        fingerprint = get_refresh_token_fingerprint(raw_token)
        token_hash = hash_token(raw_token)
        
        expired_token = RefreshToken(
            user_id=registered_user.id,
            token_fingerprint=fingerprint,
            token_hash=token_hash,
            expires_at=datetime.now(timezone.utc) - timedelta(days=1)
        )
        db_session.add(expired_token)
        db_session.commit()
        
        response = client.post(
            "/auth/refresh",
            cookies={"refresh_token": raw_token}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_refresh_with_revoked_token_deletes_all_user_tokens(self, client, db_session, registered_user):
        import uuid
        
        raw_token = uuid.uuid4().hex
        fingerprint = get_refresh_token_fingerprint(raw_token)
        token_hash = hash_token(raw_token)
        
        revoked_token = RefreshToken(
            user_id=registered_user.id,
            token_fingerprint=fingerprint,
            token_hash=token_hash,
            expires_at=datetime.now(timezone.utc) + timedelta(days=30),
            revoked_at=datetime.now(timezone.utc) - timedelta(hours=1)
        )
        
        other_token = RefreshToken(
            user_id=registered_user.id,
            token_fingerprint="other_fingerprint",
            token_hash=hash_token("other_token"),
            expires_at=datetime.now(timezone.utc) + timedelta(days=30)
        )
        
        db_session.add(revoked_token)
        db_session.add(other_token)
        db_session.commit()
        
        response = client.post(
            "/auth/refresh",
            cookies={"refresh_token": raw_token}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        stmt = select(RefreshToken).where(RefreshToken.user_id == registered_user.id)
        remaining_tokens = db_session.execute(stmt).scalars().all()
        assert len(remaining_tokens) == 0
    
    def test_refresh_creates_new_token_in_database(self, client, db_session, registered_user, logged_in_user_with_refresh_cookie):
        from sqlalchemy import func
        
        stmt = select(func.count()).select_from(RefreshToken).where(RefreshToken.user_id == registered_user.id)
        initial_count = db_session.execute(stmt).scalar()
        
        response = client.post(
            "/auth/refresh",
            cookies={"refresh_token": logged_in_user_with_refresh_cookie}
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        final_count = db_session.execute(stmt).scalar()
        assert final_count == initial_count + 1
    
    def test_refresh_multiple_times_creates_token_chain(self, client, db_session, registered_user, logged_in_user_with_refresh_cookie):
        token1 = logged_in_user_with_refresh_cookie
        
        response1 = client.post("/auth/refresh", cookies={"refresh_token": token1})
        assert response1.status_code == status.HTTP_200_OK
        token2 = response1.cookies.get("refresh_token")
        
        response2 = client.post("/auth/refresh", cookies={"refresh_token": token2})
        assert response2.status_code == status.HTTP_200_OK
        token3 = response2.cookies.get("refresh_token")
        
        assert token1 != token2 != token3
        
        stmt = select(RefreshToken).where(RefreshToken.user_id == registered_user.id)
        all_tokens = db_session.execute(stmt).scalars().all()
        assert len(all_tokens) == 3
        
        revoked_count = sum(1 for t in all_tokens if t.revoked_at is not None)
        assert revoked_count == 2
    
    def test_refresh_access_token_contains_user_id(self, client, registered_user, logged_in_user_with_refresh_cookie):
        import jwt
        from src.config.settings import get_settings
        
        response = client.post(
            "/auth/refresh",
            cookies={"refresh_token": logged_in_user_with_refresh_cookie}
        )
        
        assert response.status_code == status.HTTP_200_OK
        access_token = response.json()["access_token"]
        
        settings = get_settings()
        decoded = jwt.decode(access_token, settings.SECRET_KEY, algorithms=["HS256"])
        
        assert decoded["sub"] == str(registered_user.id)
    
    def test_refresh_with_malformed_token_returns_401(self, client):
        response = client.post(
            "/auth/refresh",
            cookies={"refresh_token": "totally_invalid"}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Not authenticated" in response.json()["detail"]
    
    def test_refresh_reuse_after_first_rotation(self, client, db_session, registered_user, logged_in_user_with_refresh_cookie):
        token1 = logged_in_user_with_refresh_cookie
        
        response1 = client.post("/auth/refresh", cookies={"refresh_token": token1})
        assert response1.status_code == status.HTTP_200_OK
        
        response2 = client.post("/auth/refresh", cookies={"refresh_token": token1})
        assert response2.status_code == status.HTTP_401_UNAUTHORIZED
        
        stmt = select(RefreshToken).where(RefreshToken.user_id == registered_user.id)
        remaining_tokens = db_session.execute(stmt).scalars().all()
        assert len(remaining_tokens) == 0
    
    def test_refresh_different_users_get_different_tokens(self, client, db_session):
        user1 = User(email="user1@example.com", password_hash=get_password_hash("Pass1!"), name="User 1", is_verified=True)
        user2 = User(email="user2@example.com", password_hash=get_password_hash("Pass2!"), name="User 2", is_verified=True)
        db_session.add(user1)
        db_session.add(user2)
        db_session.commit()
        
        response1_login = client.post("/auth/login", data={"username": "user1@example.com", "password": "Pass1!"})
        response2_login = client.post("/auth/login", data={"username": "user2@example.com", "password": "Pass2!"})
        
        token1 = response1_login.cookies.get("refresh_token")
        token2 = response2_login.cookies.get("refresh_token")
        
        response1_refresh = client.post("/auth/refresh", cookies={"refresh_token": token1})
        response2_refresh = client.post("/auth/refresh", cookies={"refresh_token": token2})
        
        assert response1_refresh.status_code == status.HTTP_200_OK
        assert response2_refresh.status_code == status.HTTP_200_OK
        
        new_access_token1 = response1_refresh.json()["access_token"]
        new_access_token2 = response2_refresh.json()["access_token"]
        
        assert new_access_token1 != new_access_token2
