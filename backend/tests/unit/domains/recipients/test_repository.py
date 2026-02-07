import pytest
import uuid
from sqlalchemy import select

from src.domains.recipients.repository import RecipientRepository
from src.domains.recipients.models import Recipient
from src.domains.users.models import User


class TestRecipientRepositoryCreate:
    
    def test_create_recipient(self, db_session):
        repo = RecipientRepository(db_session)
        
        # Create user first
        user = User(email="test@example.com", password_hash="hash", name="Test")
        db_session.add(user)
        db_session.commit()
        
        recipient = Recipient(
            user_id=user.id,
            name="Test Recipient",
            notes="Test notes"
        )
        
        created_recipient = repo.create(recipient)
        
        assert created_recipient.id is not None
        assert created_recipient.user_id == user.id
        assert created_recipient.name == "Test Recipient"
        assert created_recipient.notes == "Test notes"
    
    def test_create_recipient_without_notes(self, db_session):
        repo = RecipientRepository(db_session)
        
        user = User(email="test@example.com", password_hash="hash", name="Test")
        db_session.add(user)
        db_session.commit()
        
        recipient = Recipient(
            user_id=user.id,
            name="No Notes Recipient",
            notes=None
        )
        
        created_recipient = repo.create(recipient)
        
        assert created_recipient.id is not None
        assert created_recipient.notes is None
    
    def test_create_recipient_persists_in_db(self, db_session):
        repo = RecipientRepository(db_session)
        
        user = User(email="test@example.com", password_hash="hash", name="Test")
        db_session.add(user)
        db_session.commit()
        
        recipient = Recipient(
            user_id=user.id,
            name="Persisted Recipient",
            notes="Should persist"
        )
        
        created_recipient = repo.create(recipient)
        db_session.expire_all()
        
        stmt = select(Recipient).where(Recipient.id == created_recipient.id)
        retrieved = db_session.execute(stmt).scalar_one_or_none()
        
        assert retrieved is not None
        assert retrieved.name == "Persisted Recipient"
        assert retrieved.notes == "Should persist"


class TestRecipientRepositoryGet:
    
    def test_get_empty_list(self, db_session):
        repo = RecipientRepository(db_session)
        
        user = User(email="test@example.com", password_hash="hash", name="Test")
        db_session.add(user)
        db_session.commit()
        
        pagination = {"sort": "default", "page": 1, "limit": 10}
        recipients, total = repo.get(pagination, user.id)
        
        assert recipients == []
        assert total == 0
    
    def test_get_recipients_for_user(self, db_session):
        repo = RecipientRepository(db_session)
        
        user = User(email="test@example.com", password_hash="hash", name="Test")
        db_session.add(user)
        db_session.commit()
        
        # Create recipients
        for i in range(3):
            recipient = Recipient(user_id=user.id, name=f"Recipient {i}", notes=None)
            db_session.add(recipient)
        db_session.commit()
        
        pagination = {"sort": "default", "page": 1, "limit": 10}
        recipients, total = repo.get(pagination, user.id)
        
        assert len(recipients) == 3
        assert total == 3
    
    def test_get_recipients_filters_by_user_id(self, db_session):
        repo = RecipientRepository(db_session)
        
        user1 = User(email="user1@example.com", password_hash="hash", name="User 1")
        user2 = User(email="user2@example.com", password_hash="hash", name="User 2")
        db_session.add_all([user1, user2])
        db_session.commit()
        
        # Create recipients for both users
        recipient1 = Recipient(user_id=user1.id, name="User 1 Recipient", notes=None)
        recipient2 = Recipient(user_id=user2.id, name="User 2 Recipient", notes=None)
        db_session.add_all([recipient1, recipient2])
        db_session.commit()
        
        pagination = {"sort": "default", "page": 1, "limit": 10}
        user1_recipients, total = repo.get(pagination, user1.id)
        
        assert len(user1_recipients) == 1
        assert total == 1
        assert user1_recipients[0].name == "User 1 Recipient"
    
    def test_get_recipients_sort_ascending(self, db_session):
        repo = RecipientRepository(db_session)
        
        user = User(email="test@example.com", password_hash="hash", name="Test")
        db_session.add(user)
        db_session.commit()
        
        # Create in non-alphabetical order
        names = ["Zara", "Alice", "Bob"]
        for name in names:
            recipient = Recipient(user_id=user.id, name=name, notes=None)
            db_session.add(recipient)
        db_session.commit()
        
        pagination = {"sort": "asc", "page": 1, "limit": 10}
        recipients, total = repo.get(pagination, user.id)
        
        assert len(recipients) == 3
        assert recipients[0].name == "Alice"
        assert recipients[1].name == "Bob"
        assert recipients[2].name == "Zara"
    
    def test_get_recipients_sort_descending(self, db_session):
        repo = RecipientRepository(db_session)
        
        user = User(email="test@example.com", password_hash="hash", name="Test")
        db_session.add(user)
        db_session.commit()
        
        names = ["Zara", "Alice", "Bob"]
        for name in names:
            recipient = Recipient(user_id=user.id, name=name, notes=None)
            db_session.add(recipient)
        db_session.commit()
        
        pagination = {"sort": "desc", "page": 1, "limit": 10}
        recipients, total = repo.get(pagination, user.id)
        
        assert len(recipients) == 3
        assert recipients[0].name == "Zara"
        assert recipients[1].name == "Bob"
        assert recipients[2].name == "Alice"
    
    def test_get_recipients_pagination_limit(self, db_session):
        repo = RecipientRepository(db_session)
        
        user = User(email="test@example.com", password_hash="hash", name="Test")
        db_session.add(user)
        db_session.commit()
        
        # Create 5 recipients
        for i in range(5):
            recipient = Recipient(user_id=user.id, name=f"Recipient {i}", notes=None)
            db_session.add(recipient)
        db_session.commit()
        
        pagination = {"sort": "default", "page": 1, "limit": 2}
        recipients, total = repo.get(pagination, user.id)
        
        assert len(recipients) == 2
        assert total == 5
    
    def test_get_recipients_pagination_page_2(self, db_session):
        repo = RecipientRepository(db_session)
        
        user = User(email="test@example.com", password_hash="hash", name="Test")
        db_session.add(user)
        db_session.commit()
        
        # Create 5 recipients with sortable names
        for i in range(5):
            recipient = Recipient(user_id=user.id, name=f"Recipient {i:02d}", notes=None)
            db_session.add(recipient)
        db_session.commit()
        
        pagination = {"sort": "asc", "page": 2, "limit": 2}
        recipients, total = repo.get(pagination, user.id)
        
        assert len(recipients) == 2
        # Page 1 would have Recipient 00, 01
        # Page 2 should have Recipient 02, 03
        assert recipients[0].name == "Recipient 02"
        assert recipients[1].name == "Recipient 03"


class TestRecipientRepositoryGetById:
    
    def test_get_by_id_success(self, db_session):
        repo = RecipientRepository(db_session)
        
        user = User(email="test@example.com", password_hash="hash", name="Test")
        db_session.add(user)
        db_session.commit()
        
        recipient = Recipient(user_id=user.id, name="Test Recipient", notes="Notes")
        db_session.add(recipient)
        db_session.commit()
        
        retrieved = repo.get_by_id(user.id, recipient.id)
        
        assert retrieved is not None
        assert retrieved.id == recipient.id
        assert retrieved.name == "Test Recipient"
    
    def test_get_by_id_not_found(self, db_session):
        repo = RecipientRepository(db_session)
        
        user = User(email="test@example.com", password_hash="hash", name="Test")
        db_session.add(user)
        db_session.commit()
        
        non_existent_id = uuid.uuid4()
        retrieved = repo.get_by_id(user.id, non_existent_id)
        
        assert retrieved is None
    
    def test_get_by_id_wrong_user_returns_none(self, db_session):
        repo = RecipientRepository(db_session)
        
        user1 = User(email="user1@example.com", password_hash="hash", name="User 1")
        user2 = User(email="user2@example.com", password_hash="hash", name="User 2")
        db_session.add_all([user1, user2])
        db_session.commit()
        
        # Create recipient for user1
        recipient = Recipient(user_id=user1.id, name="User 1 Recipient", notes=None)
        db_session.add(recipient)
        db_session.commit()
        
        # Try to get with user2's ID
        retrieved = repo.get_by_id(user2.id, recipient.id)
        
        assert retrieved is None


class TestRecipientRepositoryUpdate:
    
    def test_update_recipient(self, db_session):
        repo = RecipientRepository(db_session)
        
        user = User(email="test@example.com", password_hash="hash", name="Test")
        db_session.add(user)
        db_session.commit()
        
        recipient = Recipient(user_id=user.id, name="Original Name", notes="Original Notes")
        db_session.add(recipient)
        db_session.commit()
        
        # Modify and update
        recipient.name = "Updated Name"
        recipient.notes = "Updated Notes"
        
        updated = repo.update(recipient)
        
        assert updated.name == "Updated Name"
        assert updated.notes == "Updated Notes"
    
    def test_update_recipient_persists(self, db_session):
        repo = RecipientRepository(db_session)
        
        user = User(email="test@example.com", password_hash="hash", name="Test")
        db_session.add(user)
        db_session.commit()
        
        recipient = Recipient(user_id=user.id, name="Original", notes="Original")
        db_session.add(recipient)
        db_session.commit()
        
        recipient.name = "Updated"
        repo.update(recipient)
        
        # Clear session and retrieve
        db_session.expire_all()
        stmt = select(Recipient).where(Recipient.id == recipient.id)
        retrieved = db_session.execute(stmt).scalar_one()
        
        assert retrieved.name == "Updated"


class TestRecipientRepositoryDelete:
    
    def test_delete_recipient_success(self, db_session):
        repo = RecipientRepository(db_session)
        
        user = User(email="test@example.com", password_hash="hash", name="Test")
        db_session.add(user)
        db_session.commit()
        
        recipient = Recipient(user_id=user.id, name="To Delete", notes=None)
        db_session.add(recipient)
        db_session.commit()
        recipient_id = recipient.id
        
        result = repo.delete(user.id, recipient_id)
        
        assert result is True
        
        # Verify deletion
        stmt = select(Recipient).where(Recipient.id == recipient_id)
        retrieved = db_session.execute(stmt).scalar_one_or_none()
        assert retrieved is None
    
    def test_delete_recipient_not_found(self, db_session):
        repo = RecipientRepository(db_session)
        
        user = User(email="test@example.com", password_hash="hash", name="Test")
        db_session.add(user)
        db_session.commit()
        
        non_existent_id = uuid.uuid4()
        result = repo.delete(user.id, non_existent_id)
        
        assert result is False
    
    def test_delete_recipient_wrong_user(self, db_session):
        repo = RecipientRepository(db_session)
        
        user1 = User(email="user1@example.com", password_hash="hash", name="User 1")
        user2 = User(email="user2@example.com", password_hash="hash", name="User 2")
        db_session.add_all([user1, user2])
        db_session.commit()
        
        # Create recipient for user1
        recipient = Recipient(user_id=user1.id, name="User 1 Recipient", notes=None)
        db_session.add(recipient)
        db_session.commit()
        recipient_id = recipient.id
        
        # Try to delete with user2's ID
        result = repo.delete(user2.id, recipient_id)
        
        assert result is False
        
        # Verify recipient still exists
        stmt = select(Recipient).where(Recipient.id == recipient_id)
        retrieved = db_session.execute(stmt).scalar_one_or_none()
        assert retrieved is not None
