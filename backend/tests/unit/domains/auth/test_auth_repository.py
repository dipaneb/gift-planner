import pytest
import uuid
from datetime import datetime, timezone, timedelta

from src.domains.auth.repository import RefreshTokenRepository
from src.domains.auth.models import RefreshToken


class TestRefreshTokenRepository:
    
    def test_create_refresh_token(self, db_session):
        repo = RefreshTokenRepository(db_session)
        user_id = uuid.uuid4()
        
        token = RefreshToken(
            user_id=user_id,
            token_hash="hashed_token_123",
            expires_at=datetime.now(timezone.utc) + timedelta(days=30)
        )
        
        created_token = repo.create(token)
        
        assert created_token.id is not None
        assert created_token.user_id == user_id
        assert created_token.token_hash == "hashed_token_123"
        assert created_token.created_at is not None
        assert created_token.revoked_at is None
    
    def test_create_refresh_token_persists_in_db(self, db_session):
        from sqlalchemy import select
        
        repo = RefreshTokenRepository(db_session)
        user_id = uuid.uuid4()
        
        token = RefreshToken(
            user_id=user_id,
            token_hash="unique_hash_456",
            expires_at=datetime.now(timezone.utc) + timedelta(days=30)
        )
        
        created_token = repo.create(token)
        db_session.expire_all()
        
        stmt = select(RefreshToken).where(RefreshToken.id == created_token.id)
        retrieved = db_session.execute(stmt).scalar_one_or_none()
        assert retrieved is not None
        assert retrieved.token_hash == "unique_hash_456"
        assert retrieved.user_id == user_id
    
    def test_create_multiple_refresh_tokens_for_same_user(self, db_session):
        repo = RefreshTokenRepository(db_session)
        user_id = uuid.uuid4()
        
        token1 = RefreshToken(
            user_id=user_id,
            token_hash="hash_1",
            expires_at=datetime.now(timezone.utc) + timedelta(days=30)
        )
        token2 = RefreshToken(
            user_id=user_id,
            token_hash="hash_2",
            expires_at=datetime.now(timezone.utc) + timedelta(days=30)
        )
        
        created1 = repo.create(token1)
        created2 = repo.create(token2)
        
        assert created1.id != created2.id
        assert created1.user_id == created2.user_id
        assert created1.token_hash != created2.token_hash
    
    def test_create_refresh_token_with_expiration(self, db_session):
        repo = RefreshTokenRepository(db_session)
        user_id = uuid.uuid4()
        expires_at = datetime.now(timezone.utc) + timedelta(days=7)
        
        token = RefreshToken(
            user_id=user_id,
            token_hash="expiring_token",
            expires_at=expires_at
        )
        
        created_token = repo.create(token)
        
        # SQLite returns timezone-aware datetime, compare by replacing tzinfo
        created_aware = created_token.expires_at.replace(tzinfo=timezone.utc) if created_token.expires_at.tzinfo is None else created_token.expires_at
        assert abs((created_aware - expires_at).total_seconds()) < 1
        assert created_token.expires_at.replace(tzinfo=timezone.utc) > datetime.now(timezone.utc)
