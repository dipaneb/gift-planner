from src.domains.users.repository import UserRepository
from src.domains.users.models import User


class TestUserRepositoryGetByEmail:
    
    def test_get_by_email_existing_user(self, db_session, sample_user):
        repo = UserRepository(db_session)
        result = repo.get_by_email(sample_user.email)
        assert result is not None
        assert result.email == sample_user.email
        assert result.id == sample_user.id
    
    def test_get_by_email_non_existing_user(self, db_session):
        repo = UserRepository(db_session)
        result = repo.get_by_email("nonexistent@example.com")
        assert result is None
    
    def test_get_by_email_returns_correct_user_when_multiple_exist(self, db_session):
        user1 = User(email="user1@example.com", password_hash="hash1", name="User 1")
        user2 = User(email="user2@example.com", password_hash="hash2", name="User 2")
        db_session.add(user1)
        db_session.add(user2)
        db_session.commit()
        
        repo = UserRepository(db_session)
        result = repo.get_by_email("user1@example.com")
        assert result is not None
        assert result.email == "user1@example.com"
        assert result.name == "User 1"


class TestUserRepositoryGetById:
    
    def test_get_by_id_existing_user(self, db_session, sample_user):
        repo = UserRepository(db_session)
        result = repo.get_by_id(sample_user.id)
        assert result is not None
        assert result.id == sample_user.id
        assert result.email == sample_user.email
    
    def test_get_by_id_non_existing_user(self, db_session):
        import uuid
        repo = UserRepository(db_session)
        non_existent_id = uuid.uuid4()
        result = repo.get_by_id(non_existent_id)
        assert result is None
    
    def test_get_by_id_returns_correct_user_when_multiple_exist(self, db_session):
        user1 = User(email="user1@example.com", password_hash="hash1", name="User 1")
        user2 = User(email="user2@example.com", password_hash="hash2", name="User 2")
        db_session.add(user1)
        db_session.add(user2)
        db_session.commit()
        db_session.refresh(user1)
        db_session.refresh(user2)
        
        repo = UserRepository(db_session)
        result = repo.get_by_id(user1.id)
        assert result is not None
        assert result.id == user1.id
        assert result.email == "user1@example.com"
        assert result.name == "User 1"


class TestUserRepositoryCreate:
    
    def test_create_user_success(self, db_session):
        repo = UserRepository(db_session)
        user = User(
            email="newuser@example.com",
            password_hash="hashed_password",
            name="New User"
        )
        created_user = repo.create(user)
        
        assert created_user.id is not None
        assert created_user.email == "newuser@example.com"
        assert created_user.name == "New User"
        assert created_user.password_hash == "hashed_password"
    
    def test_create_user_without_name(self, db_session):
        repo = UserRepository(db_session)
        user = User(
            email="noname@example.com",
            password_hash="hashed_password",
            name=None
        )
        created_user = repo.create(user)
        
        assert created_user.id is not None
        assert created_user.email == "noname@example.com"
        assert created_user.name is None
    
    def test_create_user_persists_to_database(self, db_session):
        repo = UserRepository(db_session)
        user = User(
            email="persist@example.com",
            password_hash="hashed_password",
            name="Persist User"
        )
        created_user = repo.create(user)
        
        db_session.expire_all()
        fetched_user = repo.get_by_email("persist@example.com")
        assert fetched_user is not None
        assert fetched_user.id == created_user.id
        assert fetched_user.email == created_user.email
    
    def test_create_user_returns_refreshed_object(self, db_session):
        repo = UserRepository(db_session)
        user = User(
            email="refresh@example.com",
            password_hash="hashed_password",
            name="Refresh User"
        )
        created_user = repo.create(user)
        
        assert hasattr(created_user, 'id')
        assert created_user.id is not None


class TestUserRepositorySetPassword:
    
    def test_set_password_updates_password_hash(self, db_session):
        repo = UserRepository(db_session)
        user = User(
            email="user@example.com",
            password_hash="old_hash",
            name="Test User"
        )
        created_user = repo.create(user)
        old_hash = created_user.password_hash
        
        repo.set_password(created_user.id, "NewSecure123!")
        
        db_session.refresh(created_user)
        assert created_user.password_hash != old_hash
        assert created_user.password_hash != "NewSecure123!"
    
    def test_set_password_hashes_new_password(self, db_session):
        repo = UserRepository(db_session)
        user = User(
            email="user@example.com",
            password_hash="old_hash",
            name="Test User"
        )
        created_user = repo.create(user)
        plain_password = "NewSecure123!"
        
        repo.set_password(created_user.id, plain_password)
        
        db_session.refresh(created_user)
        assert created_user.password_hash != plain_password
        assert len(created_user.password_hash) > 20
    
    def test_set_password_persists_to_database(self, db_session):
        repo = UserRepository(db_session)
        user = User(
            email="user@example.com",
            password_hash="old_hash",
            name="Test User"
        )
        created_user = repo.create(user)
        
        repo.set_password(created_user.id, "NewSecure123!")
        
        db_session.expire_all()
        retrieved_user = repo.get_by_id(created_user.id)
        assert retrieved_user.password_hash != "old_hash"
    
    def test_set_password_only_affects_specified_user(self, db_session):
        repo = UserRepository(db_session)
        user1 = User(email="user1@example.com", password_hash="hash1", name="User 1")
        user2 = User(email="user2@example.com", password_hash="hash2", name="User 2")
        created_user1 = repo.create(user1)
        created_user2 = repo.create(user2)
        original_hash2 = created_user2.password_hash
        
        repo.set_password(created_user1.id, "NewPassword123!")
        
        db_session.refresh(created_user1)
        db_session.refresh(created_user2)
        assert created_user1.password_hash != "hash1"
        assert created_user2.password_hash == original_hash2
    
    def test_set_password_different_passwords_produce_different_hashes(self, db_session):
        repo = UserRepository(db_session)
        user = User(
            email="user@example.com",
            password_hash="old_hash",
            name="Test User"
        )
        created_user = repo.create(user)
        
        repo.set_password(created_user.id, "Password1!")
        db_session.refresh(created_user)
        hash1 = created_user.password_hash
        
        repo.set_password(created_user.id, "Password2!")
        db_session.refresh(created_user)
        hash2 = created_user.password_hash
        
        assert hash1 != hash2
