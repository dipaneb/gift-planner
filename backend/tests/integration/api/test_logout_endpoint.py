import pytest
from fastapi import status
from sqlalchemy import select

from src.domains.users.models import User
from src.domains.auth.models import RefreshToken
from src.domains.auth.password_handler import get_password_hash


class TestLogoutEndpoint:
    
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
    
    def test_logout_success(self, client, registered_user, logged_in_user_with_refresh_cookie, db_session):
        stmt = select(RefreshToken).where(RefreshToken.user_id == registered_user.id)
        tokens_before = db_session.execute(stmt).scalars().all()
        assert len(tokens_before) == 1
        
        response = client.post(
            "/auth/logout",
            cookies={"refresh_token": logged_in_user_with_refresh_cookie}
        )
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        tokens_after = db_session.execute(stmt).scalars().all()
        assert len(tokens_after) == 0
    
    def test_logout_clears_cookie(self, client, logged_in_user_with_refresh_cookie):
        response = client.post(
            "/auth/logout",
            cookies={"refresh_token": logged_in_user_with_refresh_cookie}
        )
        
        cookies = response.headers.get("set-cookie", "")
        
        assert "refresh_token=" in cookies.lower()
        assert "path=/auth" in cookies.lower()
    
    def test_logout_without_cookie(self, client):
        response = client.post("/auth/logout")
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        cookies = response.headers.get("set-cookie", "")
        assert "refresh_token=" in cookies.lower()
    
    def test_logout_with_invalid_token(self, client):
        response = client.post(
            "/auth/logout",
            cookies={"refresh_token": "invalid_token_value"}
        )
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        cookies = response.headers.get("set-cookie", "")
        assert "refresh_token=" in cookies.lower()
    
    def test_logout_deletes_all_user_tokens(self, client, registered_user, db_session):
        login_response1 = client.post(
            "/auth/login",
            data={
                "username": "john@example.com",
                "password": "SecurePass123!"
            }
        )
        token1 = login_response1.cookies.get("refresh_token")
        
        login_response2 = client.post(
            "/auth/login",
            data={
                "username": "john@example.com",
                "password": "SecurePass123!"
            }
        )
        
        stmt = select(RefreshToken).where(RefreshToken.user_id == registered_user.id)
        tokens_before = db_session.execute(stmt).scalars().all()
        assert len(tokens_before) == 2
        
        client.post(
            "/auth/logout",
            cookies={"refresh_token": token1}
        )
        
        tokens_after = db_session.execute(stmt).scalars().all()
        assert len(tokens_after) == 0
    
    def test_logout_with_expired_token_still_deletes_all_tokens(self, client, registered_user, db_session):
        from datetime import datetime, timezone, timedelta
        from src.domains.auth.refresh_token_handler import hash_token, get_refresh_token_fingerprint
        
        raw_token = "expired_token_abc123"
        token_fingerprint = get_refresh_token_fingerprint(raw_token)
        token_hash = hash_token(raw_token)
        
        expired_token = RefreshToken(
            user_id=registered_user.id,
            token_fingerprint=token_fingerprint,
            token_hash=token_hash,
            expires_at=datetime.now(timezone.utc) - timedelta(days=1)
        )
        db_session.add(expired_token)
        db_session.commit()
        
        response = client.post(
            "/auth/logout",
            cookies={"refresh_token": raw_token}
        )
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        stmt = select(RefreshToken).where(RefreshToken.user_id == registered_user.id)
        tokens_after = db_session.execute(stmt).scalars().all()
        assert len(tokens_after) == 0
    
    def test_logout_with_wrong_token_hash_does_not_delete(self, client, registered_user, db_session):
        from datetime import datetime, timezone, timedelta
        from src.domains.auth.refresh_token_handler import get_refresh_token_fingerprint, hash_token
        
        raw_token = "token_with_wrong_hash"
        token_fingerprint = get_refresh_token_fingerprint(raw_token)
        wrong_hash = hash_token("completely_different_token")
        
        token = RefreshToken(
            user_id=registered_user.id,
            token_fingerprint=token_fingerprint,
            token_hash=wrong_hash,
            expires_at=datetime.now(timezone.utc) + timedelta(days=30)
        )
        db_session.add(token)
        db_session.commit()
        
        response = client.post(
            "/auth/logout",
            cookies={"refresh_token": raw_token}
        )
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        stmt = select(RefreshToken).where(RefreshToken.user_id == registered_user.id)
        tokens_after = db_session.execute(stmt).scalars().all()
        assert len(tokens_after) == 1
