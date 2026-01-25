import pytest
import uuid
from datetime import datetime, timezone, timedelta

from src.domains.auth.repository import ResetPasswordRepository
from src.domains.auth.models import PasswordResetToken
from src.domains.users.models import User


class TestResetPasswordRepositoryCreate:
    
    @pytest.fixture
    def sample_user(self, db_session):
        user = User(
            email="test@example.com",
            password_hash="hash",
            name="Test User"
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user
    
    def test_create_reset_token_success(self, db_session, sample_user):
        repo = ResetPasswordRepository(db_session)
        token = PasswordResetToken(
            user_id=sample_user.id,
            token_fingerprint="fingerprint_123",
            token_hash="hash_123",
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1)
        )
        
        created_token = repo.create(token)
        
        assert created_token.id is not None
        assert created_token.user_id == sample_user.id
        assert created_token.token_fingerprint == "fingerprint_123"
        assert created_token.token_hash == "hash_123"
    
    def test_create_reset_token_persists_to_database(self, db_session, sample_user):
        repo = ResetPasswordRepository(db_session)
        token = PasswordResetToken(
            user_id=sample_user.id,
            token_fingerprint="fingerprint_xyz",
            token_hash="hash_xyz",
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1)
        )
        
        created_token = repo.create(token)
        
        db_session.expire_all()
        
        from sqlalchemy import select
        stmt = select(PasswordResetToken).where(PasswordResetToken.id == created_token.id)
        fetched_token = db_session.execute(stmt).scalar_one_or_none()
        
        assert fetched_token is not None
        assert fetched_token.id == created_token.id
        assert fetched_token.token_fingerprint == "fingerprint_xyz"
    
    def test_create_multiple_tokens_for_same_user(self, db_session, sample_user):
        repo = ResetPasswordRepository(db_session)
        
        token1 = PasswordResetToken(
            user_id=sample_user.id,
            token_fingerprint="fingerprint_1",
            token_hash="hash_1",
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1)
        )
        token2 = PasswordResetToken(
            user_id=sample_user.id,
            token_fingerprint="fingerprint_2",
            token_hash="hash_2",
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1)
        )
        
        created1 = repo.create(token1)
        created2 = repo.create(token2)
        
        assert created1.id != created2.id
        assert created1.user_id == created2.user_id
    
    def test_create_reset_token_with_correct_expiration(self, db_session, sample_user):
        repo = ResetPasswordRepository(db_session)
        expected_expiration = datetime.now(timezone.utc) + timedelta(minutes=30)
        
        token = PasswordResetToken(
            user_id=sample_user.id,
            token_fingerprint="fingerprint_exp",
            token_hash="hash_exp",
            expires_at=expected_expiration
        )
        
        created_token = repo.create(token)
        
        created_expiration = created_token.expires_at
        if created_expiration.tzinfo is None:
            created_expiration = created_expiration.replace(tzinfo=timezone.utc)
        
        time_diff = abs((created_expiration - expected_expiration).total_seconds())
        assert time_diff < 2
    
    def test_create_reset_token_used_at_is_none(self, db_session, sample_user):
        repo = ResetPasswordRepository(db_session)
        token = PasswordResetToken(
            user_id=sample_user.id,
            token_fingerprint="fingerprint_unused",
            token_hash="hash_unused",
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1)
        )
        
        created_token = repo.create(token)
        
        assert created_token.used_at is None


class TestResetPasswordRepositoryGetByFingerprint:
    
    @pytest.fixture
    def sample_user(self, db_session):
        user = User(
            email="test@example.com",
            password_hash="hash123",
            name="Test User"
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user
    
    def test_get_by_fingerprint_existing_token(self, db_session, sample_user):
        repo = ResetPasswordRepository(db_session)
        token = PasswordResetToken(
            user_id=sample_user.id,
            token_fingerprint="unique_fingerprint",
            token_hash="hash_value",
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1)
        )
        created = repo.create(token)
        
        retrieved = repo.get_by_fingerprint("unique_fingerprint")
        
        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.token_fingerprint == "unique_fingerprint"
    
    def test_get_by_fingerprint_non_existing_token(self, db_session):
        repo = ResetPasswordRepository(db_session)
        
        retrieved = repo.get_by_fingerprint("non_existent_fingerprint")
        
        assert retrieved is None
    
    def test_get_by_fingerprint_returns_correct_token_when_multiple_exist(self, db_session, sample_user):
        repo = ResetPasswordRepository(db_session)
        token1 = PasswordResetToken(
            user_id=sample_user.id,
            token_fingerprint="fingerprint_1",
            token_hash="hash_1",
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1)
        )
        token2 = PasswordResetToken(
            user_id=sample_user.id,
            token_fingerprint="fingerprint_2",
            token_hash="hash_2",
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1)
        )
        repo.create(token1)
        created2 = repo.create(token2)
        
        retrieved = repo.get_by_fingerprint("fingerprint_2")
        
        assert retrieved is not None
        assert retrieved.id == created2.id
        assert retrieved.token_fingerprint == "fingerprint_2"


class TestResetPasswordRepositoryMarkUsed:
    
    @pytest.fixture
    def sample_user(self, db_session):
        user = User(
            email="test@example.com",
            password_hash="hash123",
            name="Test User"
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user
    
    def test_mark_used_sets_used_at_timestamp(self, db_session, sample_user):
        repo = ResetPasswordRepository(db_session)
        token = PasswordResetToken(
            user_id=sample_user.id,
            token_fingerprint="fingerprint_used",
            token_hash="hash_used",
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1)
        )
        created = repo.create(token)
        assert created.used_at is None
        
        before_mark = datetime.now(timezone.utc)
        repo.mark_used(created.id)
        after_mark = datetime.now(timezone.utc)
        
        db_session.refresh(created)
        assert created.used_at is not None
        
        used_at = created.used_at
        if used_at.tzinfo is None:
            used_at = used_at.replace(tzinfo=timezone.utc)
        
        assert before_mark <= used_at <= after_mark
    
    def test_mark_used_persists_to_database(self, db_session, sample_user):
        repo = ResetPasswordRepository(db_session)
        token = PasswordResetToken(
            user_id=sample_user.id,
            token_fingerprint="fingerprint_persist",
            token_hash="hash_persist",
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1)
        )
        created = repo.create(token)
        
        repo.mark_used(created.id)
        
        db_session.expire_all()
        retrieved = repo.get_by_fingerprint("fingerprint_persist")
        assert retrieved.used_at is not None
    
    def test_mark_used_only_affects_specified_token(self, db_session, sample_user):
        repo = ResetPasswordRepository(db_session)
        token1 = PasswordResetToken(
            user_id=sample_user.id,
            token_fingerprint="fingerprint_a",
            token_hash="hash_a",
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1)
        )
        token2 = PasswordResetToken(
            user_id=sample_user.id,
            token_fingerprint="fingerprint_b",
            token_hash="hash_b",
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1)
        )
        created1 = repo.create(token1)
        created2 = repo.create(token2)
        
        repo.mark_used(created1.id)
        
        db_session.refresh(created1)
        db_session.refresh(created2)
        assert created1.used_at is not None
        assert created2.used_at is None
    
    def test_create_reset_token_has_created_at(self, db_session, sample_user):
        repo = ResetPasswordRepository(db_session)
        token = PasswordResetToken(
            user_id=sample_user.id,
            token_fingerprint="fingerprint_created",
            token_hash="hash_created",
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1)
        )
        
        created_token = repo.create(token)
        
        assert created_token.created_at is not None
        assert isinstance(created_token.created_at, datetime)
