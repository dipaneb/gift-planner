import pytest
from datetime import datetime, timezone, timedelta
from fastapi import status
from sqlalchemy import select

from src.domains.users.models import User
from src.domains.auth.models import PasswordResetToken, RefreshToken
from src.domains.auth.password_handler import get_password_hash, verify_password
from src.domains.auth.reset_password_token_handler import hash_token as hash_reset_token, get_reset_password_token_fingerprint
from src.domains.auth.refresh_token_handler import hash_token as hash_refresh_token, get_refresh_token_fingerprint


class TestResetPasswordEndpoint:
    
    @pytest.fixture
    def registered_user(self, db_session):
        user = User(
            email="john@example.com",
            password_hash=get_password_hash("OldPassword123!"),
            name="John Doe"
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user
    
    @pytest.fixture
    def valid_reset_token(self, db_session, registered_user):
        raw_token = "valid_reset_token_12345"
        token_hash = hash_reset_token(raw_token)
        token_fingerprint = get_reset_password_token_fingerprint(raw_token)
        
        reset_token = PasswordResetToken(
            user_id=registered_user.id,
            token_fingerprint=token_fingerprint,
            token_hash=token_hash,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1)
        )
        db_session.add(reset_token)
        db_session.commit()
        db_session.refresh(reset_token)
        return raw_token
    
    def test_reset_password_success(self, client, registered_user, valid_reset_token, db_session):
        response = client.post(
            f"/auth/reset-password?token={valid_reset_token}",
            json={
                "password": "NewPassword123!",
                "confirmed_password": "NewPassword123!"
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert "password updated" in data["message"].lower()
        
        db_session.refresh(registered_user)
        assert verify_password("NewPassword123!", registered_user.password_hash)
        assert not verify_password("OldPassword123!", registered_user.password_hash)
    
    def test_reset_password_marks_token_as_used(self, client, registered_user, valid_reset_token, db_session):
        client.post(
            f"/auth/reset-password?token={valid_reset_token}",
            json={
                "password": "NewPassword123!",
                "confirmed_password": "NewPassword123!"
            }
        )
        
        token_fingerprint = get_reset_password_token_fingerprint(valid_reset_token)
        stmt = select(PasswordResetToken).where(PasswordResetToken.token_fingerprint == token_fingerprint)
        reset_token = db_session.execute(stmt).scalar_one()
        
        assert reset_token.used_at is not None
    
    def test_reset_password_invalidates_all_refresh_tokens(self, client, registered_user, valid_reset_token, db_session):
        raw_refresh_token = "refresh_token_123"
        refresh_token = RefreshToken(
            user_id=registered_user.id,
            token_fingerprint=get_refresh_token_fingerprint(raw_refresh_token),
            token_hash=hash_refresh_token(raw_refresh_token),
            expires_at=datetime.now(timezone.utc) + timedelta(days=30)
        )
        db_session.add(refresh_token)
        db_session.commit()
        
        client.post(
            f"/auth/reset-password?token={valid_reset_token}",
            json={
                "password": "NewPassword123!",
                "confirmed_password": "NewPassword123!"
            }
        )
        
        stmt = select(RefreshToken).where(RefreshToken.user_id == registered_user.id)
        remaining_tokens = db_session.execute(stmt).scalars().all()
        assert len(remaining_tokens) == 0
    
    def test_reset_password_with_invalid_token(self, client):
        response = client.post(
            "/auth/reset-password?token=invalid_token",
            json={
                "password": "NewPassword123!",
                "confirmed_password": "NewPassword123!"
            }
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "invalid" in data["detail"].lower() or "expired" in data["detail"].lower()
    
    def test_reset_password_with_expired_token(self, client, db_session, registered_user):
        raw_token = "expired_token_12345"
        token_hash = hash_reset_token(raw_token)
        token_fingerprint = get_reset_password_token_fingerprint(raw_token)
        
        expired_token = PasswordResetToken(
            user_id=registered_user.id,
            token_fingerprint=token_fingerprint,
            token_hash=token_hash,
            expires_at=datetime.now(timezone.utc) - timedelta(hours=1)
        )
        db_session.add(expired_token)
        db_session.commit()
        
        response = client.post(
            f"/auth/reset-password?token={raw_token}",
            json={
                "password": "NewPassword123!",
                "confirmed_password": "NewPassword123!"
            }
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_reset_password_with_used_token(self, client, db_session, registered_user):
        raw_token = "used_token_12345"
        token_hash = hash_reset_token(raw_token)
        token_fingerprint = get_reset_password_token_fingerprint(raw_token)
        
        used_token = PasswordResetToken(
            user_id=registered_user.id,
            token_fingerprint=token_fingerprint,
            token_hash=token_hash,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
            used_at=datetime.now(timezone.utc) - timedelta(minutes=10)
        )
        db_session.add(used_token)
        db_session.commit()
        
        response = client.post(
            f"/auth/reset-password?token={raw_token}",
            json={
                "password": "NewPassword123!",
                "confirmed_password": "NewPassword123!"
            }
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_reset_password_password_mismatch(self, client, valid_reset_token):
        response = client.post(
            f"/auth/reset-password?token={valid_reset_token}",
            json={
                "password": "NewPassword123!",
                "confirmed_password": "DifferentPassword123!"
            }
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_reset_password_weak_password(self, client, valid_reset_token):
        response = client.post(
            f"/auth/reset-password?token={valid_reset_token}",
            json={
                "password": "weak",
                "confirmed_password": "weak"
            }
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_reset_password_missing_uppercase(self, client, valid_reset_token):
        response = client.post(
            f"/auth/reset-password?token={valid_reset_token}",
            json={
                "password": "password123!",
                "confirmed_password": "password123!"
            }
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_reset_password_missing_password_field(self, client, valid_reset_token):
        response = client.post(
            f"/auth/reset-password?token={valid_reset_token}",
            json={
                "confirmed_password": "NewPassword123!"
            }
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_reset_password_missing_token_query_param(self, client):
        response = client.post(
            "/auth/reset-password",
            json={
                "password": "NewPassword123!",
                "confirmed_password": "NewPassword123!"
            }
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_reset_password_with_wrong_token_hash(self, client, db_session, registered_user):
        raw_token = "correct_token_12345"
        wrong_raw_token = "wrong_token_12345"
        token_hash = hash_reset_token(raw_token)
        token_fingerprint = get_reset_password_token_fingerprint(wrong_raw_token)
        
        reset_token = PasswordResetToken(
            user_id=registered_user.id,
            token_fingerprint=token_fingerprint,
            token_hash=token_hash,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1)
        )
        db_session.add(reset_token)
        db_session.commit()
        
        response = client.post(
            f"/auth/reset-password?token={wrong_raw_token}",
            json={
                "password": "NewPassword123!",
                "confirmed_password": "NewPassword123!"
            }
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
