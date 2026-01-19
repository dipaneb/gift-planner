import pytest
import uuid
from datetime import datetime, timezone, timedelta
from sqlalchemy import select

from src.domains.auth.repository import RefreshTokenRepository
from src.domains.auth.models import RefreshToken


class TestRefreshTokenRepositoryCreate:
    
    def test_create_refresh_token(self, db_session):
        repo = RefreshTokenRepository(db_session)
        user_id = uuid.uuid4()
        
        token = RefreshToken(
            user_id=user_id,
            token_fingerprint="fingerprint_123",
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
        repo = RefreshTokenRepository(db_session)
        user_id = uuid.uuid4()
        
        token = RefreshToken(
            user_id=user_id,
            token_fingerprint="unique_fingerprint_456",
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
            token_fingerprint="fingerprint_1",
            token_hash="hash_1",
            expires_at=datetime.now(timezone.utc) + timedelta(days=30)
        )
        token2 = RefreshToken(
            user_id=user_id,
            token_fingerprint="fingerprint_2",
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
            token_fingerprint="expiring_fingerprint",
            token_hash="expiring_token",
            expires_at=expires_at
        )
        
        created_token = repo.create(token)
        
        created_aware = created_token.expires_at.replace(tzinfo=timezone.utc) if created_token.expires_at.tzinfo is None else created_token.expires_at
        assert abs((created_aware - expires_at).total_seconds()) < 1
        assert created_token.expires_at.replace(tzinfo=timezone.utc) > datetime.now(timezone.utc)


class TestRefreshTokenRepositoryGetByFingerprint:
    
    def test_get_by_fingerprint_existing_token(self, db_session):
        repo = RefreshTokenRepository(db_session)
        user_id = uuid.uuid4()
        
        token = RefreshToken(
            user_id=user_id,
            token_fingerprint="abc123fingerprint",
            token_hash="hashed_value",
            expires_at=datetime.now(timezone.utc) + timedelta(days=30)
        )
        db_session.add(token)
        db_session.commit()
        
        result = repo.get_by_fingerprint("abc123fingerprint")
        
        assert result is not None
        assert result.token_fingerprint == "abc123fingerprint"
        assert result.user_id == user_id
    
    def test_get_by_fingerprint_non_existing_token(self, db_session):
        repo = RefreshTokenRepository(db_session)
        
        result = repo.get_by_fingerprint("nonexistent_fingerprint")
        
        assert result is None
    
    def test_get_by_fingerprint_with_multiple_tokens(self, db_session):
        repo = RefreshTokenRepository(db_session)
        user_id = uuid.uuid4()
        
        token1 = RefreshToken(
            user_id=user_id,
            token_fingerprint="fingerprint1",
            token_hash="hash1",
            expires_at=datetime.now(timezone.utc) + timedelta(days=30)
        )
        token2 = RefreshToken(
            user_id=user_id,
            token_fingerprint="fingerprint2",
            token_hash="hash2",
            expires_at=datetime.now(timezone.utc) + timedelta(days=30)
        )
        db_session.add(token1)
        db_session.add(token2)
        db_session.commit()
        
        result = repo.get_by_fingerprint("fingerprint2")
        
        assert result is not None
        assert result.token_fingerprint == "fingerprint2"
        assert result.token_hash == "hash2"


class TestRefreshTokenRepositoryRevoke:
    
    def test_revoke_token_sets_revoked_at(self, db_session):
        repo = RefreshTokenRepository(db_session)
        user_id = uuid.uuid4()
        
        token = RefreshToken(
            user_id=user_id,
            token_fingerprint="test_fingerprint",
            token_hash="test_hash",
            expires_at=datetime.now(timezone.utc) + timedelta(days=30)
        )
        created_token = repo.create(token)
        
        assert created_token.revoked_at is None
        
        repo.revoke(created_token.id)
        
        stmt = select(RefreshToken).where(RefreshToken.id == created_token.id)
        revoked_token = db_session.execute(stmt).scalar_one_or_none()
        
        assert revoked_token.revoked_at is not None
        revoked_aware = revoked_token.revoked_at.replace(tzinfo=timezone.utc) if revoked_token.revoked_at.tzinfo is None else revoked_token.revoked_at
        assert revoked_aware <= datetime.now(timezone.utc)
    
    def test_revoke_token_with_replaced_by_id(self, db_session):
        repo = RefreshTokenRepository(db_session)
        user_id = uuid.uuid4()
        
        old_token = RefreshToken(
            user_id=user_id,
            token_fingerprint="old_fingerprint",
            token_hash="old_hash",
            expires_at=datetime.now(timezone.utc) + timedelta(days=30)
        )
        new_token = RefreshToken(
            user_id=user_id,
            token_fingerprint="new_fingerprint",
            token_hash="new_hash",
            expires_at=datetime.now(timezone.utc) + timedelta(days=30)
        )
        old_created = repo.create(old_token)
        new_created = repo.create(new_token)
        
        repo.revoke(old_created.id, replaced_by_id=new_created.id)
        
        stmt = select(RefreshToken).where(RefreshToken.id == old_created.id)
        revoked_token = db_session.execute(stmt).scalar_one_or_none()
        
        assert revoked_token.revoked_at is not None
        assert revoked_token.replaced_by_id == new_created.id
    
    def test_revoke_token_without_replaced_by_id(self, db_session):
        repo = RefreshTokenRepository(db_session)
        user_id = uuid.uuid4()
        
        token = RefreshToken(
            user_id=user_id,
            token_fingerprint="fingerprint",
            token_hash="hash",
            expires_at=datetime.now(timezone.utc) + timedelta(days=30)
        )
        created_token = repo.create(token)
        
        repo.revoke(created_token.id)
        
        stmt = select(RefreshToken).where(RefreshToken.id == created_token.id)
        revoked_token = db_session.execute(stmt).scalar_one_or_none()
        
        assert revoked_token.replaced_by_id is None


class TestRefreshTokenRepositoryDeleteAllForUser:
    
    def test_delete_all_for_user_removes_all_tokens(self, db_session):
        repo = RefreshTokenRepository(db_session)
        user_id = uuid.uuid4()
        
        token1 = RefreshToken(
            user_id=user_id,
            token_fingerprint="fp1",
            token_hash="hash1",
            expires_at=datetime.now(timezone.utc) + timedelta(days=30)
        )
        token2 = RefreshToken(
            user_id=user_id,
            token_fingerprint="fp2",
            token_hash="hash2",
            expires_at=datetime.now(timezone.utc) + timedelta(days=30)
        )
        token3 = RefreshToken(
            user_id=user_id,
            token_fingerprint="fp3",
            token_hash="hash3",
            expires_at=datetime.now(timezone.utc) + timedelta(days=30)
        )
        
        repo.create(token1)
        repo.create(token2)
        repo.create(token3)
        
        stmt = select(RefreshToken).where(RefreshToken.user_id == user_id)
        tokens_before = db_session.execute(stmt).scalars().all()
        assert len(tokens_before) == 3
        
        repo.delete_all_for_user(user_id)
        
        tokens_after = db_session.execute(stmt).scalars().all()
        assert len(tokens_after) == 0
    
    def test_delete_all_for_user_does_not_affect_other_users(self, db_session):
        repo = RefreshTokenRepository(db_session)
        user1_id = uuid.uuid4()
        user2_id = uuid.uuid4()
        
        token1 = RefreshToken(
            user_id=user1_id,
            token_fingerprint="user1_fp",
            token_hash="user1_hash",
            expires_at=datetime.now(timezone.utc) + timedelta(days=30)
        )
        token2 = RefreshToken(
            user_id=user2_id,
            token_fingerprint="user2_fp",
            token_hash="user2_hash",
            expires_at=datetime.now(timezone.utc) + timedelta(days=30)
        )
        
        repo.create(token1)
        repo.create(token2)
        
        repo.delete_all_for_user(user1_id)
        
        stmt1 = select(RefreshToken).where(RefreshToken.user_id == user1_id)
        user1_tokens = db_session.execute(stmt1).scalars().all()
        assert len(user1_tokens) == 0
        
        stmt2 = select(RefreshToken).where(RefreshToken.user_id == user2_id)
        user2_tokens = db_session.execute(stmt2).scalars().all()
        assert len(user2_tokens) == 1
    
    def test_delete_all_for_user_with_no_tokens(self, db_session):
        repo = RefreshTokenRepository(db_session)
        user_id = uuid.uuid4()
        
        repo.delete_all_for_user(user_id)
        
        stmt = select(RefreshToken).where(RefreshToken.user_id == user_id)
        tokens = db_session.execute(stmt).scalars().all()
        assert len(tokens) == 0
