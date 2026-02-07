import pytest
import uuid
from decimal import Decimal
from sqlalchemy import select

from src.domains.gifts.repository import GiftRepository
from src.domains.gifts.models import Gift
from src.domains.gifts.enums import GiftStatusEnum
from src.domains.users.models import User
from src.domains.recipients.models import Recipient


class TestGiftRepositoryCreate:

    def test_create_gift(self, db_session):
        repo = GiftRepository(db_session)

        user = User(email="test@example.com", password_hash="hash", name="Test")
        db_session.add(user)
        db_session.commit()

        gift = Gift(
            user_id=user.id,
            name="Chess set",
            url="https://example.com",
            price=Decimal("29.99"),
            status=GiftStatusEnum.idee,
            quantity=1,
        )

        created_gift = repo.create(gift)

        assert created_gift.id is not None
        assert created_gift.user_id == user.id
        assert created_gift.name == "Chess set"
        assert created_gift.url == "https://example.com"
        assert created_gift.price == Decimal("29.99")
        assert created_gift.status == GiftStatusEnum.idee
        assert created_gift.quantity == 1

    def test_create_gift_minimal(self, db_session):
        repo = GiftRepository(db_session)

        user = User(email="test@example.com", password_hash="hash", name="Test")
        db_session.add(user)
        db_session.commit()

        gift = Gift(
            user_id=user.id,
            name="Simple gift",
        )

        created_gift = repo.create(gift)

        assert created_gift.id is not None
        assert created_gift.name == "Simple gift"
        assert created_gift.url is None
        assert created_gift.price is None

    def test_create_gift_persists_in_db(self, db_session):
        repo = GiftRepository(db_session)

        user = User(email="test@example.com", password_hash="hash", name="Test")
        db_session.add(user)
        db_session.commit()

        gift = Gift(
            user_id=user.id,
            name="Persisted Gift",
            price=Decimal("50.00"),
            status=GiftStatusEnum.achete,
            quantity=2,
        )

        created_gift = repo.create(gift)
        db_session.expire_all()

        stmt = select(Gift).where(Gift.id == created_gift.id)
        retrieved = db_session.execute(stmt).scalar_one_or_none()

        assert retrieved is not None
        assert retrieved.name == "Persisted Gift"
        assert retrieved.price == Decimal("50.00")
        assert retrieved.status == GiftStatusEnum.achete
        assert retrieved.quantity == 2


class TestGiftRepositoryGet:

    def test_get_empty_list(self, db_session):
        repo = GiftRepository(db_session)

        user = User(email="test@example.com", password_hash="hash", name="Test")
        db_session.add(user)
        db_session.commit()

        pagination = {"sort": "default", "page": 1, "limit": 10}
        gifts, total = repo.get(pagination, user.id)

        assert gifts == []
        assert total == 0

    def test_get_gifts_for_user(self, db_session):
        repo = GiftRepository(db_session)

        user = User(email="test@example.com", password_hash="hash", name="Test")
        db_session.add(user)
        db_session.commit()

        for i in range(3):
            gift = Gift(user_id=user.id, name=f"Gift {i}")
            db_session.add(gift)
        db_session.commit()

        pagination = {"sort": "default", "page": 1, "limit": 10}
        gifts, total = repo.get(pagination, user.id)

        assert len(gifts) == 3
        assert total == 3

    def test_get_gifts_filters_by_user_id(self, db_session):
        repo = GiftRepository(db_session)

        user1 = User(email="user1@example.com", password_hash="hash", name="User 1")
        user2 = User(email="user2@example.com", password_hash="hash", name="User 2")
        db_session.add_all([user1, user2])
        db_session.commit()

        gift1 = Gift(user_id=user1.id, name="User 1 Gift")
        gift2 = Gift(user_id=user2.id, name="User 2 Gift")
        db_session.add_all([gift1, gift2])
        db_session.commit()

        pagination = {"sort": "default", "page": 1, "limit": 10}
        user1_gifts, total = repo.get(pagination, user1.id)

        assert len(user1_gifts) == 1
        assert total == 1
        assert user1_gifts[0].name == "User 1 Gift"

    def test_get_gifts_sort_ascending(self, db_session):
        repo = GiftRepository(db_session)

        user = User(email="test@example.com", password_hash="hash", name="Test")
        db_session.add(user)
        db_session.commit()

        names = ["Zara gift", "Alice gift", "Bob gift"]
        for name in names:
            gift = Gift(user_id=user.id, name=name)
            db_session.add(gift)
        db_session.commit()

        pagination = {"sort": "asc", "page": 1, "limit": 10}
        gifts, total = repo.get(pagination, user.id)

        assert len(gifts) == 3
        assert gifts[0].name == "Alice gift"
        assert gifts[1].name == "Bob gift"
        assert gifts[2].name == "Zara gift"

    def test_get_gifts_sort_descending(self, db_session):
        repo = GiftRepository(db_session)

        user = User(email="test@example.com", password_hash="hash", name="Test")
        db_session.add(user)
        db_session.commit()

        names = ["Zara gift", "Alice gift", "Bob gift"]
        for name in names:
            gift = Gift(user_id=user.id, name=name)
            db_session.add(gift)
        db_session.commit()

        pagination = {"sort": "desc", "page": 1, "limit": 10}
        gifts, total = repo.get(pagination, user.id)

        assert len(gifts) == 3
        assert gifts[0].name == "Zara gift"
        assert gifts[1].name == "Bob gift"
        assert gifts[2].name == "Alice gift"

    def test_get_gifts_pagination_limit(self, db_session):
        repo = GiftRepository(db_session)

        user = User(email="test@example.com", password_hash="hash", name="Test")
        db_session.add(user)
        db_session.commit()

        for i in range(5):
            gift = Gift(user_id=user.id, name=f"Gift {i}")
            db_session.add(gift)
        db_session.commit()

        pagination = {"sort": "default", "page": 1, "limit": 2}
        gifts, total = repo.get(pagination, user.id)

        assert len(gifts) == 2
        assert total == 5

    def test_get_gifts_pagination_page_2(self, db_session):
        repo = GiftRepository(db_session)

        user = User(email="test@example.com", password_hash="hash", name="Test")
        db_session.add(user)
        db_session.commit()

        for i in range(5):
            gift = Gift(user_id=user.id, name=f"Gift {i:02d}")
            db_session.add(gift)
        db_session.commit()

        pagination = {"sort": "asc", "page": 2, "limit": 2}
        gifts, total = repo.get(pagination, user.id)

        assert len(gifts) == 2
        assert gifts[0].name == "Gift 02"
        assert gifts[1].name == "Gift 03"


class TestGiftRepositoryGetById:

    def test_get_by_id_success(self, db_session):
        repo = GiftRepository(db_session)

        user = User(email="test@example.com", password_hash="hash", name="Test")
        db_session.add(user)
        db_session.commit()

        gift = Gift(user_id=user.id, name="Test Gift", price=Decimal("25.00"))
        db_session.add(gift)
        db_session.commit()

        retrieved = repo.get_by_id(user.id, gift.id)

        assert retrieved is not None
        assert retrieved.id == gift.id
        assert retrieved.name == "Test Gift"

    def test_get_by_id_not_found(self, db_session):
        repo = GiftRepository(db_session)

        user = User(email="test@example.com", password_hash="hash", name="Test")
        db_session.add(user)
        db_session.commit()

        non_existent_id = uuid.uuid4()
        retrieved = repo.get_by_id(user.id, non_existent_id)

        assert retrieved is None

    def test_get_by_id_wrong_user_returns_none(self, db_session):
        repo = GiftRepository(db_session)

        user1 = User(email="user1@example.com", password_hash="hash", name="User 1")
        user2 = User(email="user2@example.com", password_hash="hash", name="User 2")
        db_session.add_all([user1, user2])
        db_session.commit()

        gift = Gift(user_id=user1.id, name="User 1 Gift")
        db_session.add(gift)
        db_session.commit()

        retrieved = repo.get_by_id(user2.id, gift.id)

        assert retrieved is None


class TestGiftRepositoryUpdate:

    def test_update_gift(self, db_session):
        repo = GiftRepository(db_session)

        user = User(email="test@example.com", password_hash="hash", name="Test")
        db_session.add(user)
        db_session.commit()

        gift = Gift(
            user_id=user.id,
            name="Original Name",
            price=Decimal("10.00"),
            status=GiftStatusEnum.idee,
            quantity=1,
        )
        db_session.add(gift)
        db_session.commit()

        gift.name = "Updated Name"
        gift.status = GiftStatusEnum.achete
        gift.quantity = 3

        updated = repo.update(gift)

        assert updated.name == "Updated Name"
        assert updated.status == GiftStatusEnum.achete
        assert updated.quantity == 3

    def test_update_gift_persists(self, db_session):
        repo = GiftRepository(db_session)

        user = User(email="test@example.com", password_hash="hash", name="Test")
        db_session.add(user)
        db_session.commit()

        gift = Gift(user_id=user.id, name="Original", price=Decimal("20.00"))
        db_session.add(gift)
        db_session.commit()

        gift.name = "Updated"
        repo.update(gift)

        db_session.expire_all()
        stmt = select(Gift).where(Gift.id == gift.id)
        retrieved = db_session.execute(stmt).scalar_one()

        assert retrieved.name == "Updated"


class TestGiftRepositoryDelete:

    def test_delete_gift_success(self, db_session):
        repo = GiftRepository(db_session)

        user = User(email="test@example.com", password_hash="hash", name="Test")
        db_session.add(user)
        db_session.commit()

        gift = Gift(user_id=user.id, name="To Delete")
        db_session.add(gift)
        db_session.commit()
        gift_id = gift.id

        result = repo.delete(user.id, gift_id)

        assert result is True

        stmt = select(Gift).where(Gift.id == gift_id)
        retrieved = db_session.execute(stmt).scalar_one_or_none()
        assert retrieved is None

    def test_delete_gift_not_found(self, db_session):
        repo = GiftRepository(db_session)

        user = User(email="test@example.com", password_hash="hash", name="Test")
        db_session.add(user)
        db_session.commit()

        non_existent_id = uuid.uuid4()
        result = repo.delete(user.id, non_existent_id)

        assert result is False

    def test_delete_gift_wrong_user(self, db_session):
        repo = GiftRepository(db_session)

        user1 = User(email="user1@example.com", password_hash="hash", name="User 1")
        user2 = User(email="user2@example.com", password_hash="hash", name="User 2")
        db_session.add_all([user1, user2])
        db_session.commit()

        gift = Gift(user_id=user1.id, name="User 1 Gift")
        db_session.add(gift)
        db_session.commit()
        gift_id = gift.id

        result = repo.delete(user2.id, gift_id)

        assert result is False

        stmt = select(Gift).where(Gift.id == gift_id)
        retrieved = db_session.execute(stmt).scalar_one_or_none()
        assert retrieved is not None
