from typing import Generator

from src.config.database import SessionLocal

def get_db() -> Generator:
    """FastAPI dependcy: yield a session for each request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()