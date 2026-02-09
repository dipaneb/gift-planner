import pytest
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from src.infrastructure.database.base import Base
import src.infrastructure.database.models
from src.infrastructure.database.session import get_db
from src.core.rate_limit import limiter
from src.main import app


@pytest.fixture(scope="function")
def db_engine():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(db_engine) -> Generator[Session, None, None]:
    TestingSessionLocal = sessionmaker(bind=db_engine, autoflush=False, autocommit=False)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    limiter.enabled = False
    with TestClient(app) as test_client:
        yield test_client
    limiter.enabled = True
    app.dependency_overrides.clear()


@pytest.fixture
def valid_user_data():
    return {
        "email": "test@example.com",
        "password": "SecurePass123!",
        "confirmed_password": "SecurePass123!",
        "name": "Test User"
    }


@pytest.fixture
def valid_user_data_no_name():
    return {
        "email": "test@example.com",
        "password": "SecurePass123!",
        "confirmed_password": "SecurePass123!",
        "name": None
    }


@pytest.fixture
def sample_user(db_session):
    from src.domains.users.models import User
    
    user = User(
        email="existing@example.com",
        password_hash="$2b$12$hashed_password_here",
        name="Existing User"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def authenticated_user(client, db_session):
    """Create a user and return (user, auth_headers) tuple."""
    from src.domains.users.models import User
    
    # Create user
    user_data = {
        "email": "auth@example.com",
        "password": "SecurePass123!",
        "confirmed_password": "SecurePass123!",
        "name": "Auth User"
    }
    register_response = client.post("/auth/register", json=user_data)
    assert register_response.status_code == 201
    
    # Login to get token
    login_data = {
        "username": user_data["email"],
        "password": user_data["password"]
    }
    login_response = client.post("/auth/login", data=login_data)
    assert login_response.status_code == 200
    
    access_token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # Get user from DB
    from sqlalchemy import select
    stmt = select(User).where(User.email == user_data["email"])
    user = db_session.execute(stmt).scalar_one()
    
    return user, headers


@pytest.fixture
def authenticated_user_with_recipients(client, authenticated_user):
    """Create authenticated user with 5 recipients."""
    user, headers = authenticated_user
    
    recipients = []
    for i in range(5):
        recipient_data = {
            "name": f"Recipient {i}",
            "notes": f"Notes for recipient {i}"
        }
        response = client.post("/recipients", json=recipient_data, headers=headers)
        assert response.status_code == 201
        recipients.append(response.json())
    
    return user, headers, recipients


@pytest.fixture
def other_user_with_recipients(client, db_session):
    """Create a different user with recipients (for isolation testing)."""
    from src.domains.users.models import User
    from src.domains.recipients.models import Recipient
    
    # Create other user
    other_user = User(
        email="other@example.com",
        password_hash="$2b$12$hashed_password",
        name="Other User"
    )
    db_session.add(other_user)
    db_session.commit()
    db_session.refresh(other_user)
    
    # Create recipients for other user
    recipients = []
    for i in range(3):
        recipient = Recipient(
            user_id=other_user.id,
            name=f"Other Recipient {i}",
            notes=f"Other notes {i}"
        )
        db_session.add(recipient)
        db_session.commit()
        db_session.refresh(recipient)
        recipients.append({
            "id": str(recipient.id),
            "name": recipient.name,
            "notes": recipient.notes,
            "user_id": str(recipient.user_id)
        })
    
    return other_user, recipients


@pytest.fixture
def authenticated_user_with_gifts(client, authenticated_user):
    """Create authenticated user with 5 gifts."""
    user, headers = authenticated_user

    gifts = []
    for i in range(5):
        gift_data = {
            "name": f"Gift {i}",
            "price": 10.00 + i,
            "status": "idee",
            "quantity": 1,
        }
        response = client.post("/gifts", json=gift_data, headers=headers)
        assert response.status_code == 201
        gifts.append(response.json())

    return user, headers, gifts


@pytest.fixture
def other_user_with_gifts(client, db_session):
    """Create a different user with gifts (for isolation testing)."""
    from src.domains.users.models import User
    from src.domains.gifts.models import Gift
    from src.domains.gifts.enums import GiftStatusEnum

    other_user = User(
        email="othergifts@example.com",
        password_hash="$2b$12$hashed_password",
        name="Other Gift User"
    )
    db_session.add(other_user)
    db_session.commit()
    db_session.refresh(other_user)

    gifts = []
    for i in range(3):
        gift = Gift(
            user_id=other_user.id,
            name=f"Other Gift {i}",
            status=GiftStatusEnum.idee,
            quantity=1,
        )
        db_session.add(gift)
        db_session.commit()
        db_session.refresh(gift)
        gifts.append({
            "id": str(gift.id),
            "name": gift.name,
            "user_id": str(gift.user_id),
        })

    return other_user, gifts
