import pytest
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from src.infrastructure.database.base import Base
import src.infrastructure.database.models
from src.infrastructure.database.session import get_db
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
    with TestClient(app) as test_client:
        yield test_client
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
