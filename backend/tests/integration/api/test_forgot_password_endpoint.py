import pytest
from unittest.mock import patch, Mock
from fastapi import status
from sqlalchemy import select

from src.domains.users.models import User
from src.domains.auth.models import PasswordResetToken
from src.domains.auth.password_handler import get_password_hash


class TestForgotPasswordEndpoint:
    
    @pytest.fixture
    def registered_user(self, db_session):
        user = User(
            email="john@example.com",
            password_hash=get_password_hash("SecurePass123!"),
            name="John Doe"
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user
    
    @patch('src.domains.auth.router.MailJetClient') # Note: The path string 'src.domains.auth.router.MailJetClient' must be where the class is used, not where it's defined.
    def test_forgot_password_success(self, mock_mailjet_class, client, registered_user, db_session):
        mock_mailjet_instance = Mock()
        mock_mailjet_class.return_value = mock_mailjet_instance
        
        response = client.post(
            "/auth/forgot-password",
            json={"email": "john@example.com"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert "reset link was sent" in data["message"].lower()
        
        stmt = select(PasswordResetToken).where(PasswordResetToken.user_id == registered_user.id)
        tokens = db_session.execute(stmt).scalars().all()
        assert len(tokens) == 1
    
    @patch('src.domains.auth.router.MailJetClient') # Note: The path string 'src.domains.auth.router.MailJetClient' must be where the class is used, not where it's defined.
    def test_forgot_password_nonexistent_email(self, mock_mailjet_class, client, db_session):
        mock_mailjet_instance = Mock()
        mock_mailjet_class.return_value = mock_mailjet_instance
        
        response = client.post(
            "/auth/forgot-password",
            json={"email": "nonexistent@example.com"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert "reset link was sent" in data["message"].lower()
        
        mock_mailjet_instance.send_email.assert_not_called()
    
    @patch('src.domains.auth.router.MailJetClient') # Note: The path string 'src.domains.auth.router.MailJetClient' must be where the class is used, not where it's defined.
    def test_forgot_password_creates_reset_token(self, mock_mailjet_class, client, registered_user, db_session):
        mock_mailjet_instance = Mock()
        mock_mailjet_class.return_value = mock_mailjet_instance
        
        client.post(
            "/auth/forgot-password",
            json={"email": "john@example.com"}
        )
        
        stmt = select(PasswordResetToken).where(PasswordResetToken.user_id == registered_user.id)
        token = db_session.execute(stmt).scalar_one_or_none()
        
        assert token is not None
        assert token.token_fingerprint is not None
        assert token.token_hash is not None
        assert token.expires_at is not None
        assert token.used_at is None
    
    @patch('src.domains.auth.router.MailJetClient') # Note: The path string 'src.domains.auth.router.MailJetClient' must be where the class is used, not where it's defined.
    def test_forgot_password_triggers_email_sending(self, mock_mailjet_class, client, registered_user):
        mock_mailjet_instance = Mock()
        mock_mailjet_class.return_value = mock_mailjet_instance
        
        response = client.post(
            "/auth/forgot-password",
            json={"email": "john@example.com"}
        )
        
        assert response.status_code == status.HTTP_200_OK
    
    def test_forgot_password_invalid_email_format(self, client):
        response = client.post(
            "/auth/forgot-password",
            json={"email": "not-an-email"}
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_forgot_password_missing_email_field(self, client):
        response = client.post(
            "/auth/forgot-password",
            json={}
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    @patch('src.domains.auth.router.MailJetClient') # Note: The path string 'src.domains.auth.router.MailJetClient' must be where the class is used, not where it's defined.
    def test_forgot_password_multiple_requests_create_multiple_tokens(self, mock_mailjet_class, client, registered_user, db_session):
        mock_mailjet_instance = Mock()
        mock_mailjet_class.return_value = mock_mailjet_instance
        
        client.post("/auth/forgot-password", json={"email": "john@example.com"})
        client.post("/auth/forgot-password", json={"email": "john@example.com"})
        
        stmt = select(PasswordResetToken).where(PasswordResetToken.user_id == registered_user.id)
        tokens = db_session.execute(stmt).scalars().all()
        assert len(tokens) == 2
    
    @patch('src.domains.auth.router.MailJetClient') # Note: The path string 'src.domains.auth.router.MailJetClient' must be where the class is used, not where it's defined.
    def test_forgot_password_user_without_name(self, mock_mailjet_class, client, db_session):
        mock_mailjet_instance = Mock()
        mock_mailjet_class.return_value = mock_mailjet_instance
        
        user = User(
            email="noname@example.com",
            password_hash=get_password_hash("SecurePass123!"),
            name=None
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        response = client.post(
            "/auth/forgot-password",
            json={"email": "noname@example.com"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        stmt = select(PasswordResetToken).where(PasswordResetToken.user_id == user.id)
        token = db_session.execute(stmt).scalar_one_or_none()
        assert token is not None
